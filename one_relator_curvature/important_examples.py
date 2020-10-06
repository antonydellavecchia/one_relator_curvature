from one_relator_curvature.example import Example

crisp_words = ['BABa', 'BBAba']
two_intersection_words = [
    "BBAbaBAba",
    "BAbABa",
    "BBBAba",
    "BABaBAba",
    "BBAbba",
    "BBABa"
]


if __name__ == '__main__':
    #crisp
    # single self intesecttion
    
    examples = map(lambda x: Example(crisp_words[1] + x), two_intersection_words)

    for example in examples:
        example.run()

