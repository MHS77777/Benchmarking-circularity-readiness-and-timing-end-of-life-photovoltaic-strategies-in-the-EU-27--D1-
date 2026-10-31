#!/usr/bin/env bash
# Reproduces every result, figure, table and workbook of the paper from the frozen
# API responses in data/raw/ (no network needed). ~10 minutes on a laptop.
set -euo pipefail
cd "$(dirname "$0")/code"
python3 build_panel.py
python3 fetch_layer_b_data.py
python3 layer_a.py          # includes the decomposition/DFSS consistency assertion
python3 layer_b.py
python3 layer_c_proxies.py
python3 layer_c.py
python3 synthesis.py
python3 figures_a.py && python3 figures_b.py && python3 figures_c.py
python3 make_tables.py
python3 build_workbooks.py
echo "Reproduction complete: see results/, figs/, manuscript/tables/, workbooks/"
# manuscript figure numbering (Figure_N.png in manuscript/figs) from the analysis figure files
cd ..
declare -A MAP=( [1]=fig1_availability_active_sets [2]=fig2_bump_S2 [3]=fig3_decomposition_S2 [4]=fig4_baselines_S2 [5]=fig5_clusters_S2 [6]=fig9_validation [7]=fig7_eu_wave [8]=fig8_country_waves [9]=fig10_urgency_readiness_map [10]=fig11_gap_materials [11]=fig12_activation_timeline )
for n in "${!MAP[@]}"; do cp "figs/${MAP[$n]}.png" "manuscript/figs/Figure_${n}.png"; done
cp figs/fig6_sensitivity_S2.png figs/fig13_fuzzy_scores.png manuscript/figs/
echo "manuscript/figs refreshed (Figure_1–11, S1–S2)"
