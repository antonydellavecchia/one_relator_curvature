# One Relator Curvature

## About
This project provides an api for studying regular sectional curvature of one-relator groups.
You can find slides used to present the work describing what the software has been built for 
in the files of this repository.


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

### Example Usage

### Using cli script
For solving all results in te given word range, this command stores database files in the output directory.


```one-relator-curvature solve_examples --output-dir /home/$USER/generated_examples --word-size-range 10 11```

To export polytope for a given word. Stores json for polytope in output directory


```one-relator-curvature get_polytope --word BabbAba -output-dir /home/$USER/polytope_examples```

To export polytopes for cycles of a given word. Stores json for polytope in output directory


```one-relator-curvature get_polytope --word BabbAba -output-dir /home/$USER/polytope_examples --cycles```


#### Importing as Python Module

```
from one_relator_curvature.example import Example
import matplotlib.pyplot as plt

example = Example("Babba")
example.generate_inequalities()
example.solve()
example.plot()
plt.show()
```

### Importing Polytopes into Polymake

The following code can be run as a polymake script passing the directory of any polytopes output by the commands get_polytope and get_polytopes
```

use JSON::Parse 'json_file_to_perl';
use JSON;
use Path::Class;
use application 'polytope';

sub read_inequalities_json {
  my $inequalities_file = $_[0];
  my $inequalities = json_file_to_perl ($inequalities_file);
  my $regions_inequalities = $inequalities->{"regions_inequalities"};
  my $links_inequalities = $inequalities->{"links_inequalities"};
  my $all_inequalities = ();

  push(@$all_inequalities, @$regions_inequalities);
  push(@$all_inequalities, @$links_inequalities);

  my $word_polytopes = {"regions" => new Polytope(INEQUALITIES=>$regions_inequalities),
            "links" => new Polytope(INEQUALITIES=>$links_inequalities),
            "intersection" => new Polytope(INEQUALITIES=>$all_inequalities)};

  return $word_polytopes;
}

sub main {
  my $polytopes_dir = dir($ARGV[0]);

  for my $polytope_file ($polytopes_dir->children) {
    my $word_polytopes = read_inequalities_json($polytope_file);
    my $intersection_polytope = $word_polytopes->{"intersection"};
    my $polytope_dim = $intersection_polytope->DIM;

    print "$polytope_file intersection polytope dimension $polytope_dim \n";
  }
}

main()
```



