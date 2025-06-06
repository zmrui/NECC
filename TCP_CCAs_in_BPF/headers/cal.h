#ifndef __BPF_CAL_H__
#define __BPF_CAL_H__

#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>
#include "vmlinux.h"


static __always_inline __u64 div64_u64(__u64 dividend, __u64 divisor)
{
	return dividend / divisor;
}

#define div64_ul div64_u64
#define div_u64 div64_u64
#define div64_long div64_u64

#define do_div(n, base) mydiv(&n, base)
__u32 mydiv (__u64* numer, int denom)
{
  __u64 res  = *numer / denom;
  __u32 rem = *numer % denom;
  *numer = res;
  return rem;
}


#define clamp(val, lo, hi) min((typeof(val))max(val, lo), hi)
#define min(a, b) ((a) < (b) ? (a) : (b))
#define max(a, b) ((a) > (b) ? (a) : (b))

static bool before(__u32 seq1, __u32 seq2)
{
	return (__s32)(seq1-seq2) < 0;
}
#define after(seq2, seq1) 	before(seq1, seq2)

#endif