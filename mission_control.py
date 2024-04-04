import ingest_and_stage_emails
import stage_dedupe_raw
import sentiment

def main():
    """
    Pipeline orchestrator for Phillies project
    """
    
    ingest_and_stage_emails.main()

    new_emails = stage_dedupe_raw.main()

    if new_emails == {}:
        print("no new emails to be analysed")
        return print("mission_control.py, script completed without analysing any new data.")

    sentiment.main(new_emails)
    
    return print("mission_control.py, script completed after having analysed some new data.")

if __name__ == "__main__":
    main()