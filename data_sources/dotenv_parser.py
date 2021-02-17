def get_env(file):
    try:
        env = {}
        dotenv = open(file, 'r')
        lines = dotenv.readlines()
        for line in lines:
            env[line[:line.find('=')]] = line[line.find('=') + 1:].strip()
        return env
    except Exception as e:
        print(e)
        return

def get_value(file:str, key:str):
    env = get_env(file)
    if key in env:
        return env[key]
    raise ValueError('Key: '+key+' is not defined in '+file+'!')
