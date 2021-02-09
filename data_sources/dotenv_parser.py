def get_env(file):
    try:
        env = {}
        dotenv = open(file, 'r')
        lines = dotenv.readlines()
        for line in lines:
            env[line[:line.find('=')]] = line[line.find('=') + 1:]
        return env
    except Exception as e:
        print(e)
        return