import argparse, sys, json


def load_resources():
    from models.models import analyze
    from models.gpt import gpt_feedback, gpt_generate_and_analyze

    return (
        analyze,
        gpt_feedback,
        gpt_generate_and_analyze,
    )

def print_verbose(text, verbose=False, **kwargs):
    if verbose:
        print(text, **kwargs)

def analyze_email(email_text, verbose=False, json_output=False, ai_feedback=False, ai_generation=False):
    print_verbose("Loading Resources...", verbose, end="")
    # Load all resources at once
    (
        analyze,
        gpt_feedback,
        gpt_generate,
    ) = load_resources()
    print_verbose("Done", verbose)

    print_verbose("Analyzing sentiment...", verbose, end="")
    results = analyze(email_text)
    print_verbose("Done", verbose)

    
    feedback=None
    # get ai feedback if wanted
    if ai_feedback:
        print_verbose("Generating AI Feedback...", verbose, end="")
        feedback = gpt_feedback(email_text, results)
        results['feedback'] = feedback
        print_verbose("Done", verbose)
    
    # generate ai email with feedback if given
    if ai_generation:
        feedback_input=False
        if feedback:
            feedback_input=True
        print_verbose("Generating AI Email...", verbose, end="")
        gen_email, _ = gpt_generate(email_text, analyze, feedback=feedback_input)
        results['gen_email'] = gen_email
        print_verbose("Done", verbose)
    
    if json_output:
        print_verbose("Dumping Json...", verbose)
        print(json.dumps(results, indent=4))
        print_verbose("Done", verbose)
    else:
        # main results
        print("\n=== Email Analysis Results ===")
        print(f"Sentiment: {results['sentiment_category']} (compound score: {results['sentiment_scores']['compound']:.2f})")
        print(f"Intent: {results['intent']} (confidence: {results['intent_confidence']})")
        print(f"Formality: {results['formality']}")
        print(f"Audience: {results['audience']} (confidence: {results['audience_confidence']})")

        # print the ai feedback if feedback is enabled
        print_verbose("\n=== AI Feedback ===", ai_feedback)
        print_verbose(feedback, ai_feedback)

        # print the ai generation if generation is enabled
        print_verbose("\n=== AI Email ===", ai_generation)
        print_verbose(gen_email, ai_generation)

    print_verbose("\nAnalysis complete!", verbose)
    return results

def read_from_file(filename):
    try:
        with open(filename, 'r') as f:
            email_text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    return email_text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sentify: Email Sentiment Analysis CLI")
    parser.add_argument("--file", "-f", help="Path to file containing email text")
    parser.add_argument("--text", "-t", help="Email text to analyze in cli command")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--json", "-j", action="store_true", help="Output results as JSON")
    parser.add_argument("--feedback", "-fb", action="store_true", help="Generate AI feedback")
    parser.add_argument("--gen", "-g", action="store_true", help="Generate AI email")
    args = parser.parse_args()

    if args.file:
        email_text = read_from_file(args.file)
    elif args.text:
        email_text = args.text
    else: # no input use default email
        print("No input provided. Using an example email...")
        email_text = """
        Subject: Test Email - Just Checking In
        Hi TestRecipient,
        This is just a quick test email to make sure everything is working correctly. Please feel free to ignore this.
        Thanks,
        Person
        """
    analyze_email(email_text, verbose=args.verbose, json_output=args.json, ai_feedback=args.feedback, ai_generation=args.gen)