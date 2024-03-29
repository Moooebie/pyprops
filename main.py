import pyprops_visualizer

if __name__ == '__main__':
    # adding backend runtime directory to PATH for Windows
    import os, platform
    if 'Windows' in platform.platform():
        graphviz_path = './graphviz_backend_win_amd64/bin/'
        os.environ["PATH"] += os.pathsep + graphviz_path
    
    # launch visualizer
    print('Loading the visualizer window...')
    pyprops_visualizer.load_visualizer()
