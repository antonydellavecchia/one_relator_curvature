from one_relator_curvature.example import Example

if __name__ == '__main__':
    #crisp
    words = ['BBAba', 'BBAbaa']
    examples = map(lambda x: Example(x), words)

    for example in examples:
        example.run()
        example.plot()

