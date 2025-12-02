#include "mc_core.hpp"

#include <algorithm>
#include <cmath>
#include <random>

MCResult mc_price_european(
    double S0,
    double K,
    double r,
    double sigma,
    double T,
    std::size_t n_paths,
    unsigned int seed,
    bool is_call
) {
    std::mt19937 rng(seed);
    std::normal_distribution<double> normal(0.0, 1.0);

    const double disc_factor      = std::exp(-r * T);
    const double drift            = (r - 0.5 * sigma * sigma) * T;
    const double diffusion_scale  = sigma * std::sqrt(T);

    double sum    = 0.0;
    double sum_sq = 0.0;

    for (std::size_t i = 0; i < n_paths; ++i) {
        const double Z  = normal(rng);
        const double ST = S0 * std::exp(drift + diffusion_scale * Z);

        double payoff = 0.0;
        if (is_call) {
            payoff = std::max(ST - K, 0.0);
        } else {
            payoff = std::max(K - ST, 0.0);
        }

        const double discounted = disc_factor * payoff;

        sum    += discounted;
        sum_sq += discounted * discounted;
    }

    const double n    = static_cast<double>(n_paths);
    const double mean = sum / n;

    const double mean_sq  = sum_sq / n;
    double variance       = mean_sq - mean * mean;
    if (variance < 0.0) {
        variance = 0.0;  // guard against tiny negative due to FP error
    }

    const double std_dev   = (variance > 0.0) ? std::sqrt(variance) : 0.0;
    const double std_error = (n_paths > 0) ? std_dev / std::sqrt(n) : 0.0;

    return MCResult{mean, std_error};
}
