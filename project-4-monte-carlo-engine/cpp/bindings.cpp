#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "mc_core.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_mc_core, m) {
    m.doc() = "C++ Monte Carlo pricer for European options under GBM";

    m.def(
        "mc_price_european",
        [](double S0,
           double K,
           double r,
           double sigma,
           double T,
           std::size_t n_paths,
           unsigned int seed,
           bool is_call) {
            MCResult res = mc_price_european(S0, K, r, sigma, T, n_paths, seed, is_call);
            // Return a simple dict for clarity
            py::dict out;
            out["price"] = res.price;
            out["std_error"] = res.std_error;
            return out;
        },
        py::arg("S0"),
        py::arg("K"),
        py::arg("r"),
        py::arg("sigma"),
        py::arg("T"),
        py::arg("n_paths"),
        py::arg("seed"),
        py::arg("is_call"),
        "Monte Carlo price for a European option (call/put) under GBM."
    );
}
