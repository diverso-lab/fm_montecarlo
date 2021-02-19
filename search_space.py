from graphviz import Digraph


def main():
    dot = Digraph(comment='The Round Table')
    dot.node('A', '')
    dot.node('B', '')
    dot.node('L', '')

    dot.edges(['AB', 'AL'])
    dot.edge('B', 'L', constraint='false')

    print(dot.source)

    dot.render('graph.gv', view=True)

if __name__ == '__main__':
    main()
