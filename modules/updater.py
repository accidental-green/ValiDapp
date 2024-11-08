import os
import utils
import install
import sys
import stop
import prints

def handle_update(execution, consensus, mevboost):
    print("\n\nExecution Client: ", execution.capitalize(), "\nConsensus Client: ", consensus.capitalize(), "\nMEVboost: ", mevboost.capitalize(), "\n")

    # Stop Services
    stop.stop_services(execution, consensus, consensus, mevboost)

    # Run Updates
    print("UPDATE - STEP 1: Update System")
    install.run_updates()

    # Update Execution Client if applicable
    if execution.lower() != 'empty':
        print(f"UPDATE - STEP 2: Updating Execution Client ({execution.upper()})")
        install.install_client(execution)
    else:
        print("Skipping execution client update")

    # Update Consensus Client if applicable
    if consensus.lower() != 'empty':
        print(f"UPDATE - STEP 3: Updating Consensus Client ({consensus.upper()})")
        install.install_client(consensus)
    else:
        print("Skipping consensus client update")

    # Install MEV-Boost if applicable
    if mevboost.lower() == "on":
        print("UPDATE - STEP 4: Updating MEVboost")
        install.install_mev()
    else:
        print("Skipping MEVboost installation as it is not enabled or 'EMPTY'")

    # Print & Version Check
    prints.print_updater(execution, consensus, mevboost)

# Main script entry point
if __name__ == "__main__":
    if len(sys.argv) == 4:
        execution = sys.argv[1].lower()
        consensus = sys.argv[2].lower()
        mevboost = sys.argv[3].lower()
        
        handle_update(execution, consensus, mevboost)
    else:
        print("Please provide all required parameters.")
