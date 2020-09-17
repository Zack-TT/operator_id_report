import sys
import pkg_resources

ScriptVersion = '0.1.10'

def check_requirements():
    if not (sys.version_info.major == 2 and sys.version_info.minor == 7):
        print("Script cannot be ran because your python version is incompatible.  Scripts must be ran with Python 2.7.")
        raise SystemExit

    for package in ['requests']:
        try:
            dist = pkg_resources.get_distribution(package)
        except pkg_resources.DistributionNotFound:
            print('Script cannot be ran because the required package "{}" is NOT installed'.format(package))
            raise SystemExit
