#pragma once

#include <cstddef>

struct MCResult {
    double price;
    double std_error;
};

// Monte Carlo price for a European call or put under risk–neutral GBM.
//
// If is_call is true  -> payoff = max(S_T - K, 0)
// If is_call is false -> payoff = max(K - S_T, 0)
MCResult mc_price_european(
    double S0,
    double K,
    double r,
    double sigma,
    double T,
    std::size_t n_paths,
    unsigned int seed,
    bool is_call
);
