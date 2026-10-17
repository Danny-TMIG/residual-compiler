#include <stddef.h>
int apex_ingress(const char *r, size_t n) { (void)r; (void)n; return 200; }
int apex_egress(const char *r, size_t n) { (void)r; (void)n; return 200; }
int apex_lateral(const char *r, size_t n) { (void)r; (void)n; return 0; }
int apex_federated(const char *r, size_t n) { (void)r; (void)n; return 200; }
