

def dict(project_path): ### Loads dictionary data from project/assets directory ###
    project_dict = {}
    with open('{}/assets/project_dict.txt'.format(project_path)) as f:
        for line in f:
            key, value = line.rstrip().split('::')
            if value == "False": value = False
            elif value == "True": value = True
            elif value == "None": value = None
            else:
                try: value = int(value)
                except: pass
            project_dict[key] = value
    return project_dict