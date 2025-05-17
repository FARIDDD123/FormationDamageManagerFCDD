import subprocess

subprocess.run(["python", "./data_generator_preprocces/data_generator.py"])
subprocess.run(["python", "./data_generator_preprocces/unique_values.py"])
subprocess.run(["python", "./data_generator_preprocces/outliers.py"])
subprocess.run(["python", "./data_generator_preprocces/missing_values.py"])
subprocess.run(["python", "./data_generator_preprocces/invalid_combination.py"])
subprocess.run(["python", "./data_generator_preprocces/normalize.py"])
