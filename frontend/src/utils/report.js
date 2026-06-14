export function downloadTextReport(result) {
  if (!result) return;

  const lines = [
    'DermAI — Skin Analysis Report',
    '================================',
    '',
    `Date: ${new Date(result.timestamp || Date.now()).toLocaleString()}`,
    `File: ${result.file}`,
    '',
    'PREDICTION',
    `Condition: ${result.prediction}`,
    `Confidence: ${(result.confidence * 100).toFixed(1)}%`,
    `Risk Level: ${result.risk_level || result.insights?.risk?.level || 'N/A'}`,
    '',
    'ALL PROBABILITIES',
    ...Object.entries(result.all_probabilities || {})
      .sort(([, a], [, b]) => b - a)
      .map(([cls, prob]) => `  ${cls}: ${(prob * 100).toFixed(1)}%`),
  ];

  if (result.insights) {
    lines.push(
      '',
      'DESCRIPTION',
      result.insights.description,
      '',
      'WHEN TO SEE A DOCTOR',
      result.insights.when_to_see_doctor,
      '',
      'CARE TIPS',
      ...result.insights.care_tips.map((t) => `  • ${t}`),
      '',
      'DISCLAIMER',
      result.insights.disclaimer,
    );
  }

  const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `dermai-report-${result.id || Date.now()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}
