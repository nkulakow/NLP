import re
from datetime import datetime
from typing import Dict, Tuple


class ReportEvaluator:
    """
    Evaluates investment reports across 5 dimensions:
    1. Structure (25%) - Completeness of required sections
    2. Data Richness (25%) - Quantity and diversity of data
    3. Professional Sophistication (20%) - Academic/professional language quality
    4. Actionability (20%) - Clear recommendations and targets
    5. Sentiment Balance (10%) - Balance of positive/negative language
    """

    def __init__(self):
        """Initialize evaluator with grading thresholds."""
        self.grade_thresholds = {
            'A': 90,  # 90-100: Excellent
            'B': 70,  # 70-89: Good
            'C': 50,  # 50-69: Satisfactory
            'D': 30,  # 30-49: Needs Improvement
            'F': 0    # 0-29: Poor
        }

    def evaluate(self, report_text: str, stock_symbol: str = "") -> Dict:
        """
        Evaluate a report and return comprehensive results.

        Args:
            report_text: The investment report text to evaluate
            stock_symbol: Stock ticker symbol (optional, for metadata)

        Returns:
            Dictionary with evaluation results including:
            - overall_score: Quality score 0-100
            - grade: Letter grade A-F
            - dimension_scores: Scores for each of 5 dimensions
            - metrics: Detailed metrics for each dimension
            - recommendations: List of improvement suggestions
        """
        # Calculate all dimension scores
        structure_score, structure_metrics = self._evaluate_structure(report_text)
        data_score, data_metrics = self._evaluate_data_richness(report_text)
        sophistication_score, sophistication_metrics = self._evaluate_sophistication(report_text)
        actionability_score, actionability_metrics = self._evaluate_actionability(report_text)
        sentiment_score, sentiment_metrics = self._evaluate_sentiment(report_text)

        # Calculate weighted overall score
        overall_score = (
            structure_score * 0.25 +
            data_score * 0.25 +
            sophistication_score * 0.20 +
            actionability_score * 0.20 +
            sentiment_score * 0.10
        )

        # Assign letter grade
        grade = self._assign_grade(overall_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            structure_score, data_score, sophistication_score,
            actionability_score, sentiment_score, report_text
        )

        return {
            'stock_symbol': stock_symbol,
            'evaluation_date': datetime.now().isoformat(),
            'overall_score': round(overall_score, 2),
            'grade': grade,
            'dimension_scores': {
                'structure': round(structure_score, 1),
                'data_richness': round(data_score, 1),
                'sophistication': round(sophistication_score, 1),
                'actionability': round(actionability_score, 1),
                'sentiment_balance': round(sentiment_score, 1)
            },
            'metrics': {
                'structure': structure_metrics,
                'data_richness': data_metrics,
                'sophistication': sophistication_metrics,
                'actionability': actionability_metrics,
                'sentiment': sentiment_metrics,
                'basic': {
                    'word_count': len(report_text.split()),
                    'character_count': len(report_text)
                }
            },
            'recommendations': recommendations
        }

    def _evaluate_structure(self, text: str) -> Tuple[float, Dict]:
        """Evaluate document structure (0-100 scale)."""
        required_sections = {
            'Executive Summary': r'executive summary|overview',
            'Sentiment Analysis': r'sentiment|market sentiment|public opinion',
            'Technical Analysis': r'technical analysis|technical indicators|chart analysis',
            'Fundamental Analysis': r'fundamental analysis|financial analysis|company analysis',
            'Risk Assessment': r'risk assessment|risk factors|risks|concerns',
            'Convergences/Divergences': r'convergence|divergence|convergences|divergences|align|contrast',
            'Catalysts': r'catalyst|catalysts|driver|drivers|growth factor',
            'Final Recommendation': r'final recommendation|recommendation|rating|action|verdict|investment outlook|outlook'
        }

        sections_found = {}
        for section_name, pattern in required_sections.items():
            sections_found[section_name] = bool(re.search(pattern, text, re.IGNORECASE))

        sections_coverage = sum(sections_found.values()) / len(required_sections)

        # Count structural elements
        markdown_headers = len(re.findall(r'^#{1,3}\s+.+$', text, re.MULTILINE))
        bold_headers = len(re.findall(r'^\*\*[^*]+\*\*:?\s*$', text, re.MULTILINE))
        headers = markdown_headers + bold_headers
        
        paragraphs = len([p for p in text.split('\n\n') if len(p.strip()) > 50])

        # Calculate structure score (0-100)
        score = (
            sections_coverage * 0.6 +
            min(headers / 10, 1) * 0.2 +
            min(paragraphs / 15, 1) * 0.2
        ) * 100

        metrics = {
            'sections_found': sections_found,
            'sections_coverage': f"{sections_coverage * 100:.0f}%",
            'total_sections': sum(sections_found.values()),
            'headers_count': headers,
            'paragraphs': paragraphs,
            'missing_sections': [k for k, v in sections_found.items() if not v]
        }

        return score, metrics

    def _evaluate_data_richness(self, text: str) -> Tuple[float, Dict]:
        """Evaluate data quantity and diversity (0-100 scale)."""
        # Extract various data types
        numbers = re.findall(r'\b\d+\.?\d*%?\b', text)
        percentages = re.findall(r'\d+\.?\d*%', text)
        dollar_amounts = re.findall(r'\$\d+\.?\d*[BMK]?', text)
        dates = re.findall(
            r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b|'
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
            text
        )

        # Financial metrics
        financial_metrics = [
            # Valuation Ratios
            'P/E', 'Price/Earnings', 'P/S', 'Price-to-Sales', 'P/B', 'Price-to-Book', 
            
            # Profitability Metrics
            'EPS', 'ROE', 'ROA', 'ROI', 'EBITDA', 'EBIT', 'Profit Margin',
            'Operating Margin', 'Gross Margin', 'Net Margin',
            
            # Growth Metrics
            'Revenue', 'Revenue Growth', 'Earnings Growth', 'EPS Growth',
            'Year-over-Year', 'YoY', 'QoQ', 'Quarter-over-Quarter',
            
            # Financial Health
            'Debt-to-Equity', 'D/E', 'Current Ratio', 'Total Debt',
            'Cash Flow', 'Free Cash Flow', 'FCF', 'Operating Cash Flow',
            
            # Market Metrics
            'Market Cap', 'Market Capitalization', 'Volume',
            
            # Dividend Metrics
            'Dividend', 'Dividend Yield', 'Dividend Growth',
            
            # Technical Indicators
            'RSI', 'MACD', 'SMA', 'Moving Average', 'EMA', 'Exponential Moving Average',
            
            # Other
            'Beta', 'Volatility', 'Analysts', 'Target Price', 'Price Target',
            'Rating', 'Recommendation'
        ]

        # Count metrics (case-insensitive)
        text_lower = text.lower()
        metrics_found = []
        for metric in financial_metrics:
            if metric.lower() in text_lower:
                metrics_found.append(metric)

        metrics_found = list(dict.fromkeys(metrics_found))

        # Source citations
        citations = len(re.findall(
            r'according to|source:|based on|reported by'
            r'analysts say|analysts project|analysts estimate|'
            r'yahoo finance|analyst|data shows|research indicates',
            text,
            re.IGNORECASE
        ))

        # Calculate data richness score (0-100)
        score = min(100, 0.5 * len(numbers) + 3 * len(metrics_found) + 8 * citations)

        # Data density
        word_count = len(text.split())
        data_density = (len(numbers) + len(dates) + citations) / word_count if word_count > 0 else 0

        metrics = {
            'total_numbers': len(numbers),
            'percentages': len(percentages),
            'dollar_amounts': len(dollar_amounts),
            'dates_mentioned': len(dates),
            'financial_metrics_count': len(metrics_found),
            'financial_metrics': metrics_found,
            'citations': citations,
            'data_density': f"{data_density * 100:.2f}%"
        }

        return score, metrics

    def _evaluate_sophistication(self, text: str) -> Tuple[float, Dict]:
        """Evaluate professional sophistication using inverted Flesch Reading Ease (0-100 scale)."""
        # Count sentences
        sentences = text.count('.') + text.count('!') + text.count('?')
        if sentences == 0:
            sentences = 1

        # Count words
        words = len(text.split())
        if words == 0:
            return 0, {
                'sophistication_score': 0,
                'interpretation': 'No text',
                'flesch_score': 0,
                'sentences': 0,
                'words': 0
            }

        # Count syllables
        syllables = sum(self._count_syllables(word) for word in text.split())

        # Flesch Reading Ease formula
        flesch_score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        flesch_score = max(0, min(100, flesch_score))

        # INVERT: Professional Sophistication = 100 - Flesch
        sophistication_score = 100 - flesch_score

        # Interpret sophistication level
        if sophistication_score >= 70:  # Flesch 0-30: Very Difficult
            interpretation = "Highly Professional (academic/expert level)"
            level_assessment = "Excellent - Advanced academic language"
        elif sophistication_score >= 50:  # Flesch 30-50: Difficult
            interpretation = "Professional (college level)"
            level_assessment = "Good - Appropriate professional tone"
        elif sophistication_score >= 40:  # Flesch 50-60: Fairly Difficult
            interpretation = "Semi-Professional (high school+)"
            level_assessment = "Acceptable - Slightly informal"
        elif sophistication_score >= 20:  # Flesch 60-80: Easy
            interpretation = "Conversational (elementary level)"
            level_assessment = "Too Simple - Lacks professional depth"
        else:  # Flesch 80-100: Very Easy
            interpretation = "Very Simple (basic level)"
            level_assessment = "Poor - Inappropriate for professional reports"

        metrics = {
            'sophistication_score': round(sophistication_score, 1),
            'flesch_score': round(flesch_score, 1),
            'interpretation': interpretation,
            'level_assessment': level_assessment,
            'sentences': sentences,
            'words': words,
            'syllables': syllables,
            'avg_words_per_sentence': round(words / sentences, 1),
            'avg_syllables_per_word': round(syllables / words, 2)
        }

        return sophistication_score, metrics

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word."""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1

        # Ensure at least 1 syllable
        if syllable_count == 0:
            syllable_count = 1

        return syllable_count

    def _evaluate_actionability(self, text: str) -> Tuple[float, Dict]:
        """Evaluate actionability of recommendations (0-100 scale)."""
        action_words = {
            'buy': ['buy', 'purchase', 'accumulate', 'long position'],
            'sell': ['sell', 'short', 'exit', 'reduce position'],
            'hold': ['hold', 'maintain', 'keep', 'neutral']
        }

        text_lower = text.lower()
        actions_found = {}

        for action, keywords in action_words.items():
            count = sum(text_lower.count(keyword) for keyword in keywords)
            actions_found[action] = count

        # Find price targets and time horizons
        price_targets = re.findall(r'price target|target price|fair value', text, re.IGNORECASE)
        time_horizons = re.findall(
            r'\d+[-\s](?:day|week|month|year)|short[- ]term|medium[- ]term|long[- ]term',
            text,
            re.IGNORECASE
        )

        # Check for clear recommendation
        has_clear_recommendation = (
            any(actions_found.values()) and
            (len(price_targets) > 0 or len(time_horizons) > 0)
        )

        # Calculate actionability score (0-100)
        score = (
            (1 if has_clear_recommendation else 0) * 40 +
            (min(len(price_targets), 2) / 2) * 30 +
            (min(len(time_horizons), 2) / 2) * 30
        )

        metrics = {
            'buy_mentions': actions_found['buy'],
            'sell_mentions': actions_found['sell'],
            'hold_mentions': actions_found['hold'],
            'primary_action': max(actions_found, key=actions_found.get) if any(actions_found.values()) else 'None',
            'has_price_target': len(price_targets) > 0,
            'price_targets_count': len(price_targets),
            'has_time_horizon': len(time_horizons) > 0,
            'time_horizons_count': len(time_horizons),
            'has_clear_recommendation': has_clear_recommendation
        }

        return score, metrics

    def _evaluate_sentiment(self, text: str) -> Tuple[float, Dict]:
        """Evaluate sentiment balance (0-100 scale, 100 = perfectly neutral)."""
        positive_words = [
            'growth', 'strong', 'increase', 'profit', 'gain', 'bullish',
            'opportunity', 'positive', 'success', 'excellent', 'outperform',
            'buy', 'upside', 'momentum', 'robust', 'solid'
        ]

        negative_words = [
            'decline', 'weak', 'decrease', 'loss', 'risk', 'bearish',
            'concern', 'negative', 'fail', 'poor', 'underperform',
            'sell', 'downside', 'volatility', 'threat', 'challenge'
        ]

        text_lower = text.lower()

        positive_count = sum(text_lower.count(word) for word in positive_words)
        negative_count = sum(text_lower.count(word) for word in negative_words)

        total = positive_count + negative_count
        if total == 0:
            sentiment_balance = 0
            sentiment_label = 'Neutral'
        else:
            sentiment_balance = (positive_count - negative_count) / total

            if sentiment_balance > 0.2:
                sentiment_label = 'Bullish'
            elif sentiment_balance < -0.2:
                sentiment_label = 'Bearish'
            else:
                sentiment_label = 'Neutral'

        # Score: 100 for perfectly neutral, decreasing as balance becomes extreme
        score = 100 - (abs(sentiment_balance) * 100)

        metrics = {
            'positive_words': positive_count,
            'negative_words': negative_count,
            'sentiment_balance': round(sentiment_balance, 3),
            'sentiment_label': sentiment_label
        }

        return score, metrics

    def _assign_grade(self, score: float) -> str:
        """Assign letter grade based on score."""
        for grade, threshold in self.grade_thresholds.items():
            if score >= threshold:
                return grade
        return 'F'

    def _generate_recommendations(
        self,
        structure_score: float,
        data_score: float,
        sophistication_score: float,
        actionability_score: float,
        sentiment_score: float,
        text: str
    ) -> list:
        """Generate actionable improvement recommendations."""
        recommendations = []

        # Structure recommendations
        if structure_score < 70:
            recommendations.append({
                'category': 'Structure',
                'priority': 'High',
                'issue': 'Missing required sections',
                'suggestion': 'Ensure report includes all 7 required sections: Executive Summary, Sentiment Analysis, Technical Analysis, Fundamental Analysis, Risk Factors, Investment Outlook, and Recommendation.'
            })

        # Data richness recommendations
        if data_score < 40:
            recommendations.append({
                'category': 'Data Richness',
                'priority': 'High',
                'issue': 'Insufficient quantitative data',
                'suggestion': 'Add more specific numbers, financial metrics (P/E, RSI, ROE), and cite at least 3 sources. Current citation count is too low.'
            })

        # Professional sophistication recommendations
        if sophistication_score < 40:
            recommendations.append({
                'category': 'Professional Sophistication',
                'priority': 'High',
                'issue': f'Language too simplistic (Sophistication: {sophistication_score:.1f}/100)',
                'suggestion': 'Elevate language to professional/academic level: Use longer, more complex sentences (25+ words), incorporate technical financial terminology, and adopt formal analytical tone. Target Sophistication score 50-70 for professional reports.'
            })
        elif sophistication_score < 50:
            recommendations.append({
                'category': 'Professional Sophistication',
                'priority': 'Medium',
                'issue': 'Language slightly informal for professional report',
                'suggestion': 'Consider using more sophisticated financial terminology and complex sentence structures to reach target Sophistication score of 50-70.'
            })

        # Actionability recommendations
        if actionability_score < 60:
            recommendations.append({
                'category': 'Actionability',
                'priority': 'High',
                'issue': 'Unclear or missing recommendation',
                'suggestion': 'Provide clear investment recommendation (Buy/Sell/Hold) with specific price target and time horizon (e.g., "Buy with target $150-160 over 6-12 months").'
            })

        # Sentiment balance recommendations
        if sentiment_score < 70:
            recommendations.append({
                'category': 'Sentiment Balance',
                'priority': 'Low',
                'issue': 'Language is too one-sided',
                'suggestion': 'Balance positive and negative language to maintain objectivity. Consider presenting both bull and bear cases.'
            })

        # If no recommendations, add positive feedback
        if not recommendations:
            recommendations.append({
                'category': 'Overall',
                'priority': 'Info',
                'issue': 'Excellent quality',
                'suggestion': 'Report meets all quality standards. Professional language, comprehensive data, clear structure, and actionable recommendations. No major improvements needed.'
            })

        return recommendations