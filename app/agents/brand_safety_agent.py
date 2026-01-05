from transformers import pipeline

class BrandSafetyAgent:
    def __init__(self):
        # Use a pre-trained model for zero-shot classification
        # This model is great for classifying text without needing to be retrained
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Define the labels for brand safety analysis.
        # We can easily add more later.
        self.safety_labels = [
            "safe content",
            "hate speech",
            "profanity",
            "political content",
            "spam",
            "adult content"
        ]

    def analyze_text(self, text: str) -> dict:
        """
        Analyzes a piece of text and returns a brand safety assessment.
        """
        if not text or not isinstance(text, str):
            return {"brand_safety_score": 1.0, "flags": []}

        try:
            # The model will return a score for each label
            results = self.classifier(text, self.safety_labels, multi_label=True)
            
            scores = dict(zip(results['labels'], results['scores']))
            
            # The safety score is 1 minus the max score of any "unsafe" category
            unsafe_scores = [
                scores[label] for label in self.safety_labels if label != "safe content"
            ]
            
            brand_safety_score = 1.0 - max(unsafe_scores)
            
            # Flag any category with a score above a certain threshold (e.g., 0.6)
            flags = [
                label for label, score in scores.items() 
                if label != "safe content" and score > 0.6
            ]

            return {
                "brand_safety_score": float(brand_safety_score),
                "flags": flags
            }
        except Exception as e:
            print(f"⚠️ Error during brand safety analysis: {e}")
            # Default to a safe score if analysis fails
            return {"brand_safety_score": 1.0, "flags": []}

# Example usage:
if __name__ == '__main__':
    agent = BrandSafetyAgent()
    
    # Example of a safe text
    safe_text = "Check out my new video on the best home fitness workouts!"
    safe_analysis = agent.analyze_text(safe_text)
    print(f"Analysis for safe text: {safe_analysis}")

    # Example of a potentially unsafe text
    unsafe_text = "This political debate is getting heated and full of hate."
    unsafe_analysis = agent.analyze_text(unsafe_text)
    print(f"Analysis for unsafe text: {unsafe_analysis}")

