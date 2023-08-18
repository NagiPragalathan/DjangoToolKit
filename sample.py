import argparse

# Create an ArgumentParser
parser = argparse.ArgumentParser(description='Process some input.')

parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')

# Add an argument for the "--base" flag
parser.add_argument('--base', type=int, help='Base value')

# Parse the command-line arguments
args = parser.parse_args()

# Check if the "--base" argument is provided
if args.base is not None:
    print(f'Base value is: {args.base}')
else:
    print('Base value not provided.')
