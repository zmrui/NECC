#define BEGIN_SOURCE_CODE 3
#include "bpf_tracing_net.h"
#include <bpf/bpf_tracing.h>

char _license[] SEC("license") = "GPL";

#define U32_MAX		((__u32)~0U)

#define ALPHA_SHIFT	7
#define ALPHA_SCALE	(1u<<ALPHA_SHIFT)
#define ALPHA_MIN	((3*ALPHA_SCALE)/10)	/* ~0.3 */
#define ALPHA_MAX	(10*ALPHA_SCALE)	/* 10.0 */
#define ALPHA_BASE	ALPHA_SCALE		/* 1.0 */
#define RTT_MAX		(U32_MAX / ALPHA_MAX)	/* 3.3 secs */

#define BETA_SHIFT	6
#define BETA_SCALE	(1u<<BETA_SHIFT)
#define BETA_MIN	(BETA_SCALE/8)		/* 0.125 */
#define BETA_MAX	(BETA_SCALE/2)		/* 0.5 */
#define BETA_BASE	BETA_MAX

static int win_thresh = 15;
static int theta = 5;

/* TCP Illinois Parameters */
struct illinois {
	__u64	sum_rtt;	/* sum of rtt's measured within last rtt */
	__u16	cnt_rtt;	/* # of rtts measured within last rtt */
	__u32	base_rtt;	/* min of all rtt in usec */
	__u32	max_rtt;	/* max of all rtt in usec */
	__u32	end_seq;	/* right edge of current RTT */
	__u32	alpha;		/* Additive increase */
	__u32	beta;		/* Muliplicative decrease */
	__u16	acked;		/* # packets acked by current ACK */
	__u8	rtt_above;	/* average rtt has gone above threshold */
	__u8	rtt_low;	/* # of rtts measurements below threshold */
};

static void rtt_reset(struct sock *sk)
{
	struct tcp_sock *tp = tcp_sk(sk);
	struct illinois *ca = inet_csk_ca(sk);

	ca->end_seq = tp->snd_nxt;
	ca->cnt_rtt = 0;
	ca->sum_rtt = 0;

	/* TODO: age max_rtt? */
}
SEC("struct_ops")
void BPF_PROG(bpf_illinois_init,struct sock *sk)
{
	struct illinois *ca = inet_csk_ca(sk);

	ca->alpha = ALPHA_MAX;
	ca->beta = BETA_BASE;
	ca->base_rtt = 0x7fffffff;
	ca->max_rtt = 0;

	ca->acked = 0;
	ca->rtt_low = 0;
	ca->rtt_above = 0;

	rtt_reset(sk);
}

/* Measure RTT for each ack. */
SEC("struct_ops")
void BPF_PROG(bpf_illinois_acked, struct sock *sk, const struct ack_sample *sample)
{
	struct illinois *ca = inet_csk_ca(sk);
	s32 rtt_us = sample->rtt_us;

	ca->acked = sample->pkts_acked;

	/* dup ack, no rtt sample */
	if (rtt_us < 0)
		return;

	/* ignore bogus values, this prevents wraparound in alpha math */
	if (rtt_us > RTT_MAX)
		rtt_us = RTT_MAX;

	/* keep track of minimum RTT seen so far */
	if (ca->base_rtt > rtt_us)
		ca->base_rtt = rtt_us;

	/* and max */
	if (ca->max_rtt < rtt_us)
		ca->max_rtt = rtt_us;

	++ca->cnt_rtt;
	ca->sum_rtt += rtt_us;
}

/* Maximum queuing delay */
static inline __u32 max_delay(const struct illinois *ca)
{
	return ca->max_rtt - ca->base_rtt;
}

/* Average queuing delay */
static inline __u32 avg_delay(const struct illinois *ca)
{
	__u64 t = ca->sum_rtt;

	do_div(t, ca->cnt_rtt);
	return t - ca->base_rtt;
}

/*
 * Compute value of alpha used for additive increase.
 * If small window then use 1.0, equivalent to Reno.
 *
 * For larger windows, adjust based on average delay.
 * A. If average delay is at minimum (we are uncongested),
 *    then use large alpha (10.0) to increase faster.
 * B. If average delay is at maximum (getting congested)
 *    then use small alpha (0.3)
 *
 * The result is a convex window growth curve.
 */
static __u32 alpha(struct illinois *ca, __u32 da, __u32 dm)
{
	__u32 d1 = dm / 100;	/* Low threshold */

	if (da <= d1) {
		/* If never got out of low delay zone, then use max */
		if (!ca->rtt_above)
			return ALPHA_MAX;

		/* Wait for 5 good RTT's before allowing alpha to go alpha max.
		 * This prevents one good RTT from causing sudden window increase.
		 */
		if (++ca->rtt_low < theta)
			return ca->alpha;

		ca->rtt_low = 0;
		ca->rtt_above = 0;
		return ALPHA_MAX;
	}

	ca->rtt_above = 1;

	/*
	 * Based on:
	 *
	 *      (dm - d1) amin amax
	 * k1 = -------------------
	 *         amax - amin
	 *
	 *       (dm - d1) amin
	 * k2 = ----------------  - d1
	 *        amax - amin
	 *
	 *             k1
	 * alpha = ----------
	 *          k2 + da
	 */

	dm -= d1;
	da -= d1;
	return (dm * ALPHA_MAX) /
		(dm + (da  * (ALPHA_MAX - ALPHA_MIN)) / ALPHA_MIN);
}

/*
 * Beta used for multiplicative decrease.
 * For small window sizes returns same value as Reno (0.5)
 *
 * If delay is small (10% of max) then beta = 1/8
 * If delay is up to 80% of max then beta = 1/2
 * In between is a linear function
 */
static __u32 beta(__u32 da, __u32 dm)
{
	__u32 d2, d3;

	d2 = dm / 10;
	if (da <= d2)
		return BETA_MIN;

	d3 = (8 * dm) / 10;
	if (da >= d3 || d3 <= d2)
		return BETA_MAX;

	/*
	 * Based on:
	 *
	 *       bmin d3 - bmax d2
	 * k3 = -------------------
	 *         d3 - d2
	 *
	 *       bmax - bmin
	 * k4 = -------------
	 *         d3 - d2
	 *
	 * b = k3 + k4 da
	 */
	return (BETA_MIN * d3 - BETA_MAX * d2 + (BETA_MAX - BETA_MIN) * da)
		/ (d3 - d2);
}

/* Update alpha and beta values once per RTT */
static void update_params(struct sock *sk)
{
	struct tcp_sock *tp = tcp_sk(sk);
	struct illinois *ca = inet_csk_ca(sk);

	if (tcp_snd_cwnd(tp) < win_thresh) {
		ca->alpha = ALPHA_BASE;
		ca->beta = BETA_BASE;
	} else if (ca->cnt_rtt > 0) {
		__u32 dm = max_delay(ca);
		__u32 da = avg_delay(ca);

		ca->alpha = alpha(ca, da, dm);
		ca->beta = beta(da, dm);
	}

	rtt_reset(sk);
}

/*
 * In case of loss, reset to default values
 */
SEC("struct_ops")
void BPF_PROG(bpf_illinois_state, struct sock *sk, __u8 new_state)
{
	struct illinois *ca = inet_csk_ca(sk);

	if (new_state == TCP_CA_Loss) {
		ca->alpha = ALPHA_BASE;
		ca->beta = BETA_BASE;
		ca->rtt_low = 0;
		ca->rtt_above = 0;
		rtt_reset(sk);
	}
}

/*
 * Increase window in response to successful acknowledgment.
 */
SEC("struct_ops")
void BPF_PROG (bpf_illinois_cong_avoid, struct sock *sk, __u32 ack, __u32 acked)
{
	struct tcp_sock *tp = tcp_sk(sk);
	struct illinois *ca = inet_csk_ca(sk);

	if (after(ack, ca->end_seq))
		update_params(sk);

	/* RFC2861 only increase cwnd if fully utilized */
	if (!tcp_is_cwnd_limited(sk))
		return;

	/* In slow start */
	if (tcp_in_slow_start(tp))
		tcp_slow_start(tp, acked);

	else {
		__u32 delta;

		/* snd_cwnd_cnt is # of packets since last cwnd increment */
		tp->snd_cwnd_cnt += ca->acked;
		ca->acked = 1;

		/* This is close approximation of:
		 * tp->snd_cwnd += alpha/tp->snd_cwnd
		*/
		delta = (tp->snd_cwnd_cnt * ca->alpha) >> ALPHA_SHIFT;
		if (delta >= tcp_snd_cwnd(tp)) {
			tcp_snd_cwnd_set(tp, min(tcp_snd_cwnd(tp) + delta / tcp_snd_cwnd(tp),
						 (__u32)tp->snd_cwnd_clamp));
			tp->snd_cwnd_cnt = 0;
		}
	}
}
SEC("struct_ops")
__u32 BPF_PROG(bpf_illinois_ssthresh, struct sock *sk)
{
	struct tcp_sock *tp = tcp_sk(sk);
	struct illinois *ca = inet_csk_ca(sk);
	__u32 decr;

	/* Multiplicative decrease */
	decr = (tcp_snd_cwnd(tp) * ca->beta) >> BETA_SHIFT;
	return max(tcp_snd_cwnd(tp) - decr, 2U);
}

SEC("struct_ops")
__u32 BPF_PROG(bpf_reno_undo_cwnd,struct sock *sk)
{
	const struct tcp_sock *tp = tcp_sk(sk);

	return max(tcp_snd_cwnd(tp) >> 1U, 2U);
}

SEC(".struct_ops")
struct tcp_congestion_ops bpf_illinois = {
	.init		= (void *) bpf_illinois_init,
	.ssthresh	= (void *) bpf_illinois_ssthresh,
	.undo_cwnd	= (void *) bpf_reno_undo_cwnd,
	.cong_avoid	= (void *) bpf_illinois_cong_avoid,
	.set_state	= (void *) bpf_illinois_state,
	.pkts_acked	= (void *) bpf_illinois_acked,
	.name		= "bpf_illinois",
};
#define END_SOURCE_CODE 3