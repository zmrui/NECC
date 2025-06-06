#define BEGIN_SOURCE_CODE 3
#include "bpf_tracing_net.h"
#include <bpf/bpf_tracing.h>



char _license[] SEC("license") = "GPL";

static int alpha = 2;
static int beta  = 4;
static int gamma = 1;

struct vegas {
	__u32	beg_snd_nxt;	/* right edge during last RTT */
	__u32	beg_snd_una;	/* left edge  during last RTT */
	__u32	beg_snd_cwnd;	/* saves the size of the cwnd */
	__u8	doing_vegas_now;/* if true, do vegas for this RTT */
	__u16	cntRTT;		/* # of RTTs measured within last RTT */
	__u32	minRTT;		/* min of RTTs measured within last RTT (in usec) */
	__u32	baseRTT;	/* the min of all Vegas RTT measurements seen (in usec) */
};

static void vegas_enable(struct sock *sk)
{
	const struct tcp_sock *tp = tcp_sk(sk);
	struct vegas *vegas = inet_csk_ca(sk);

	/* Begin taking Vegas samples next time we send something. */
	vegas->doing_vegas_now = 1;

	/* Set the beginning of the next send window. */
	vegas->beg_snd_nxt = tp->snd_nxt;

	vegas->cntRTT = 0;
	vegas->minRTT = 0x7fffffff;
}

/* Stop taking Vegas samples for now. */
static inline void vegas_disable(struct sock *sk)
{
	struct vegas *vegas = inet_csk_ca(sk);

	vegas->doing_vegas_now = 0;
}

void tcp_vegas_init(struct sock *sk)
{
	struct vegas *vegas = inet_csk_ca(sk);

	vegas->baseRTT = 0x7fffffff;
	vegas_enable(sk);
}
SEC("struct_ops")
void BPF_PROG (bpf_vegas_init, struct sock *sk)

{
	struct vegas *vegas = inet_csk_ca(sk);

	vegas->baseRTT = 0x7fffffff;
	vegas_enable(sk);
}


/* Do RTT sampling needed for Vegas.
 * Basically we:
 *   o min-filter RTT samples from within an RTT to get the current
 *     propagation delay + queuing delay (we are min-filtering to try to
 *     avoid the effects of delayed ACKs)
 *   o min-filter RTT samples from a much longer window (forever for now)
 *     to find the propagation delay (baseRTT)
 */
SEC("struct_ops")
void BPF_PROG (bpf_vegas_pkts_acked, struct sock *sk, const struct ack_sample *sample)
// void tcp_vegas_pkts_acked(struct sock *sk, const struct ack_sample *sample)
{
	struct vegas *vegas = inet_csk_ca(sk);
	__u32 vrtt;

	if (sample->rtt_us < 0)
		return;

	/* Never allow zero rtt or baseRTT */
	vrtt = sample->rtt_us + 1;

	/* Filter to find propagation delay: */
	if (vrtt < vegas->baseRTT)
		vegas->baseRTT = vrtt;

	/* Find the min RTT during the last RTT to find
	 * the current prop. delay + queuing delay:
	 */
	vegas->minRTT = min(vegas->minRTT, vrtt);
	vegas->cntRTT++;
}

SEC("struct_ops")
void BPF_PROG (bpf_vegas_state, struct sock *sk, __u8 ca_state)
{
	if (ca_state == TCP_CA_Open)
		vegas_enable(sk);
	else
		vegas_disable(sk);
}

/*
 * If the connection is idle and we are restarting,
 * then we don't want to do any Vegas calculations
 * until we get fresh RTT samples.  So when we
 * restart, we reset our Vegas state to a clean
 * slate. After we get acks for this flight of
 * packets, _then_ we can make Vegas calculations
 * again.
 */

SEC("struct_ops")
void BPF_PROG(bpf_vegas_cwnd_event, struct sock *sk, enum tcp_ca_event event)
{
	if (event == CA_EVENT_CWND_RESTART ||
	    event == CA_EVENT_TX_START)
		tcp_vegas_init(sk);
}
// EXPORT_SYMBOL_GPL(tcp_vegas_cwnd_event);

static inline __u32 tcp_vegas_ssthresh(struct tcp_sock *tp)
{
	return  min(tp->snd_ssthresh, tcp_snd_cwnd(tp));
}


// 	/* In "safe" area, increase. */
// 	if (tcp_in_slow_start(tp)) {
// 		acked = tcp_slow_start(tp, acked);
// 		if (!acked)
// 			return;
// 	}
// 	/* In dangerous area, increase slowly. */
// 	tcp_cong_avoid_ai(tp, tcp_snd_cwnd(tp), acked);
// }
SEC("struct_ops")
void BPF_PROG (bpf_vegas_cong_avoid, struct sock *sk, __u32 ack, __u32 acked)
{
	struct tcp_sock *tp = tcp_sk(sk);
	struct vegas *vegas = inet_csk_ca(sk);

	if (!vegas->doing_vegas_now) {
		// tcp_reno_cong_avoid(sk, ack, acked);
			if (!tcp_is_cwnd_limited(sk))
			return;

			/* In "safe" area, increase. */
			if (tcp_in_slow_start(tp)) {
				acked = tcp_slow_start(tp, acked);
				if (!acked)
					return;
			}
			/* In dangerous area, increase slowly. */
			tcp_cong_avoid_ai(tp, tcp_snd_cwnd(tp), acked);
		return;
	}

	if (after(ack, vegas->beg_snd_nxt)) {
		/* Do the Vegas once-per-RTT cwnd adjustment. */

		/* Save the extent of the current window so we can use this
		 * at the end of the next RTT.
		 */
		vegas->beg_snd_nxt  = tp->snd_nxt;

		/* We do the Vegas calculations only if we got enough RTT
		 * samples that we can be reasonably sure that we got
		 * at least one RTT sample that wasn't from a delayed ACK.
		 * If we only had 2 samples total,
		 * then that means we're getting only 1 ACK per RTT, which
		 * means they're almost certainly delayed ACKs.
		 * If  we have 3 samples, we should be OK.
		 */

		if (vegas->cntRTT <= 2) {
			/* We don't have enough RTT samples to do the Vegas
			 * calculation, so we'll behave like Reno.
			 */
			// tcp_reno_cong_avoid(sk, ack, acked);
				if (!tcp_is_cwnd_limited(sk))
				return;

				/* In "safe" area, increase. */
				if (tcp_in_slow_start(tp)) {
					acked = tcp_slow_start(tp, acked);
					if (!acked)
						return;
				}
				/* In dangerous area, increase slowly. */
				tcp_cong_avoid_ai(tp, tcp_snd_cwnd(tp), acked);

		} else {
			__u32 rtt, diff;
			__u64 target_cwnd;

			/* We have enough RTT samples, so, using the Vegas
			 * algorithm, we determine if we should increase or
			 * decrease cwnd, and by how much.
			 */

			/* Pluck out the RTT we are using for the Vegas
			 * calculations. This is the min RTT seen during the
			 * last RTT. Taking the min filters out the effects
			 * of delayed ACKs, at the cost of noticing congestion
			 * a bit later.
			 */
			rtt = vegas->minRTT;

			/* Calculate the cwnd we should have, if we weren't
			 * going too fast.
			 *
			 * This is:
			 *     (actual rate in segments) * baseRTT
			 */
			target_cwnd = (__u64)tcp_snd_cwnd(tp) * vegas->baseRTT;
			do_div(target_cwnd, rtt);

			/* Calculate the difference between the window we had,
			 * and the window we would like to have. This quantity
			 * is the "Diff" from the Arizona Vegas papers.
			 */
			diff = tcp_snd_cwnd(tp) * (rtt-vegas->baseRTT) / vegas->baseRTT;

			if (diff > gamma && tcp_in_slow_start(tp)) {
				/* Going too fast. Time to slow down
				 * and switch to congestion avoidance.
				 */

				/* Set cwnd to match the actual rate
				 * exactly:
				 *   cwnd = (actual rate) * baseRTT
				 * Then we add 1 because the integer
				 * truncation robs us of full link
				 * utilization.
				 */
				tcp_snd_cwnd_set(tp, min(tcp_snd_cwnd(tp),
							 (__u32)target_cwnd + 1));
				tp->snd_ssthresh = tcp_vegas_ssthresh(tp);

			} else if (tcp_in_slow_start(tp)) {
				/* Slow start.  */
				tcp_slow_start(tp, acked);
			} else {
				/* Congestion avoidance. */

				/* Figure out where we would like cwnd
				 * to be.
				 */
				if (diff > beta) {
					/* The old window was too fast, so
					 * we slow down.
					 */
					tcp_snd_cwnd_set(tp, tcp_snd_cwnd(tp) - 1);
					tp->snd_ssthresh
						= tcp_vegas_ssthresh(tp);
				} else if (diff < alpha) {
					/* We don't have enough extra packets
					 * in the network, so speed up.
					 */
					tcp_snd_cwnd_set(tp, tcp_snd_cwnd(tp) + 1);
				} else {
					/* Sending just as fast as we
					 * should be.
					 */
				}
			}

			if (tcp_snd_cwnd(tp) < 2)
				tcp_snd_cwnd_set(tp, 2);
			else if (tcp_snd_cwnd(tp) > tp->snd_cwnd_clamp)
				tcp_snd_cwnd_set(tp, tp->snd_cwnd_clamp);

			tp->snd_ssthresh = tcp_current_ssthresh(sk);
		}

		/* Wipe the slate clean for the next RTT. */
		vegas->cntRTT = 0;
		vegas->minRTT = 0x7fffffff;
	}
	/* Use normal slow start */
	else if (tcp_in_slow_start(tp))
		tcp_slow_start(tp, acked);
}

SEC("struct_ops")
__u32 BPF_PROG (bpf_tcp_reno_undo_cwnd, struct sock *sk)
{
	const struct tcp_sock *tp = tcp_sk(sk);

	return max(tcp_snd_cwnd(tp), tp->prior_cwnd);
}
SEC("struct_ops")
__u32 BPF_PROG ( bpf_tcp_reno_ssthresh, struct sock *sk)
{
	const struct tcp_sock *tp = tcp_sk(sk);

	return max(tcp_snd_cwnd(tp), tp->prior_cwnd);
}


SEC(".struct_ops")
struct tcp_congestion_ops bpf_vegas = {
	.init		= (void *)bpf_vegas_init,
	.ssthresh	= (void *)bpf_tcp_reno_ssthresh,
	.undo_cwnd	= (void *)bpf_tcp_reno_undo_cwnd,
	.cong_avoid	= (void *)bpf_vegas_cong_avoid,
	.pkts_acked	= (void *)bpf_vegas_pkts_acked,
	.set_state	= (void *)bpf_vegas_state,
	.cwnd_event	= (void *)bpf_vegas_cwnd_event,
	.name		= "bpf_vegas",
};
#define END_SOURCE_CODE 3