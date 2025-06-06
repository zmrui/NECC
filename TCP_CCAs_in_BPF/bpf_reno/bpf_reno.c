#define BEGIN_SOURCE_CODE 3
#include "bpf_tracing_net.h"
#include <bpf/bpf_tracing.h>

char _license[] SEC("license") = "GPL";

SEC("struct_ops")
void BPF_PROG(bpf_reno_cong_avoid,struct sock *sk, __u32 ack, __u32 acked)
// void bpf_reno_cong_avoid(struct sock *sk, u32 ack, u32 acked)
{
	struct tcp_sock *tp = tcp_sk(sk);

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
}


/* Slow start threshold is half the congestion window (min 2) */
SEC("struct_ops")
__u32 BPF_PROG(bpf_reno_ssthresh,struct sock *sk)
// u32 bpf_reno_ssthresh(struct sock *sk)
{
	const struct tcp_sock *tp = tcp_sk(sk);

	return max(tcp_snd_cwnd(tp) >> 1U, 2U);
}

SEC("struct_ops")
__u32 BPF_PROG(bpf_reno_undo_cwnd,struct sock *sk)
// u32 bpf_reno_undo_cwnd(struct sock *sk)
{
	const struct tcp_sock *tp = tcp_sk(sk);

	return max(tcp_snd_cwnd(tp), tp->prior_cwnd);
}

SEC(".struct_ops")
struct tcp_congestion_ops bpf_reno = {
	.name		= "bpf_reno",
	.ssthresh	= (void *)bpf_reno_ssthresh,
	.cong_avoid	= (void *)bpf_reno_cong_avoid,
	.undo_cwnd	= (void *)bpf_reno_undo_cwnd,
};
#define END_SOURCE_CODE 3