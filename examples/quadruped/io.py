import yaml
import os
from conversion import convert_human_to_animal

def write_animal_config(human_yaml_path):
    with open(human_yaml_path, 'r') as file:
        human_config = yaml.safe_load(file)

    animal_config = convert_human_to_animal(human_config)

    def represent_dict(dumper, data):
        return dumper.represent_mapping(yaml.resolver.Resolver.DEFAULT_MAPPING_TAG, data.items())
    yaml.add_representer(dict, represent_dict)

    output_dir = os.path.dirname(human_yaml_path)
    output_file = os.path.join(output_dir, 'animal_config.yaml')
    with open(output_file, 'w') as file:
        yaml.dump(animal_config, file, default_flow_style=False)
    print(f"Animal config has been written to {output_file}")
