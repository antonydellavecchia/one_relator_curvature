# One Relator Curvature

## About
This project provides an api for studying regular sectional curvature of one-relator groups.



## Installation

```pip install one-relator-curvature```


## Usage
There are two different ways of using the project, either through a collection of command line exposed functions, or as an imported python module

### CLI

Some function are exposed as command line tools. 

* solve_example
* solve_examples 
* get_all_cycle_data
* get_polytope
* get_polytopes

#### Example usage

```one-relator-curvature solve_examples --output-dir ~/generated_examples --word-size-range 10 11```

### Importing

```
from one_relator_curvature.example import Example
import matplotlib.pyplot as plt

example = Example("Babba")
example.generate_inequalities()
example.solve()
example.plot()
plt.show()
```


