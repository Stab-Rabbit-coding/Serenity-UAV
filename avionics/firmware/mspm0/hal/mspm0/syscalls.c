/**
 * @file    syscalls.c
 * @brief   Newlib retargeting for the bare-metal MSPM0G3507 build.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * The point of this file is `clock_gettime()`.  eProsima's `util/time.c`
 * calls it directly, and supplying it here — backed by `ser_hal_time_ns()` —
 * is what lets the entire Micro XRCE-DDS Client compile for bare metal
 * **without a single patch to the eProsima tree**.  Patching upstream would
 * have created a derivative that must be tracked and re-applied at every
 * version bump; a syscall shim costs nothing and is invisible to upstream.
 *
 * The remaining stubs are the minimum newlib needs to link.  They deliberately
 * fail rather than pretend: there is no filesystem, no process model and no
 * console on this part, and a stub that silently succeeds would hide a call
 * that should never have been made in flight code.
 */

#include "serenity/hal.h"

#include <errno.h>
#include <sys/stat.h>
#include <sys/times.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

/*
 * newlib declares the `_`-prefixed syscalls only in its own internal headers,
 * so the prototypes are restated here.  Without them -Wmissing-prototypes
 * (which this project enables fleet-wide) rejects every definition below.
 */
int clock_gettime(clockid_t clk_id, struct timespec *tp);
void *_sbrk(ptrdiff_t incr);
int _close(int fd);
int _fstat(int fd, struct stat *st);
int _isatty(int fd);
off_t _lseek(int fd, off_t off, int whence);
ssize_t _read(int fd, void *buf, size_t len);
ssize_t _write(int fd, const void *buf, size_t len);
int _getpid(void);
int _kill(int pid, int sig);
void _exit(int status) __attribute__((noreturn));
clock_t _times(struct tms *buf);

#undef errno
extern int errno;

/* Provided by the link script. */
extern char _sheap;
extern char _eheap;

/**
 * @brief POSIX clock, retargeted onto the HAL time base.
 *
 * Only `CLOCK_REALTIME` is answered, and it is served from the monotonic HAL
 * time base.  The node's own epoch is not wall-clock time and this
 * firmware never claims it is — the envelope timestamp is documented as
 * sender-monotonic microseconds, and correlating it to UTC is the ground
 * segment's job using the DDS source timestamp the Agent applies.
 */
int clock_gettime(clockid_t clk_id, struct timespec *tp) {
    if (tp == NULL) {
        errno = EFAULT;
        return -1;
    }
    /* This newlib does not define CLOCK_MONOTONIC, and the XRCE client only
     * ever asks for CLOCK_REALTIME, so that is the one clock answered. */
    if (clk_id != CLOCK_REALTIME) {
        errno = EINVAL;
        return -1;
    }

    const uint64_t ns = ser_hal_time_ns();
    tp->tv_sec = (time_t)(ns / 1000000000ULL);
    tp->tv_nsec = (long)(ns % 1000000000ULL);
    return 0;
}

/**
 * @brief Heap extension.
 *
 * The firmware makes no dynamic allocations of its own — every buffer in the
 * template is static, which is what makes the RAM budget checkable at link
 * time.  This exists only because newlib references it, and it refuses to
 * grow past the region the link script reserved.
 */
void *_sbrk(ptrdiff_t incr) {
    static char *brk;
    if (brk == NULL) {
        brk = &_sheap;
    }

    char *const prev = brk;
    if ((brk + incr) > &_eheap) {
        errno = ENOMEM;
        return (void *)-1;
    }
    brk += incr;
    return prev;
}

/* --- Stubs: no filesystem, no console, no processes ----------------------*/

int _close(int fd) {
    (void)fd;
    errno = EBADF;
    return -1;
}

int _fstat(int fd, struct stat *st) {
    (void)fd;
    (void)st;
    errno = EBADF;
    return -1;
}

int _isatty(int fd) {
    (void)fd;
    errno = EBADF;
    return 0;
}

off_t _lseek(int fd, off_t off, int whence) {
    (void)fd;
    (void)off;
    (void)whence;
    errno = EBADF;
    return (off_t)-1;
}

ssize_t _read(int fd, void *buf, size_t len) {
    (void)fd;
    (void)buf;
    (void)len;
    errno = EBADF;
    return -1;
}

/**
 * @brief Write, routed to the HAL debug channel for stdout and stderr.
 *
 * Diagnostics only.  Flight-relevant events leave the node as signed
 * telemetry, never through here.
 */
ssize_t _write(int fd, const void *buf, size_t len) {
    if ((fd != 1) && (fd != 2)) {
        errno = EBADF;
        return -1;
    }
    const char *p = (const char *)buf;
    for (size_t i = 0U; i < len; ++i) {
        ser_hal_log("%c", p[i]);
    }
    return (ssize_t)len;
}

int _getpid(void) {
    return 1;
}

int _kill(int pid, int sig) {
    (void)pid;
    (void)sig;
    errno = EINVAL;
    return -1;
}

void _exit(int status) {
    (void)status;
    /* Nothing to exit to.  Let the watchdog reset the part rather than
     * spinning silently forever. */
    for (;;) {
    }
}

clock_t _times(struct tms *buf) {
    (void)buf;
    errno = EACCES;
    return (clock_t)-1;
}
