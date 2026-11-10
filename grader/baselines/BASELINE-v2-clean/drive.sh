#!/bin/bash
R=/tmp/claude-185725/-home-hew-python-EvoAgenda/f3191739-9044-46f9-9033-89db443abdf7/scratchpad/baseline_v2
C=/tmp/claude-185725/-home-hew-python-EvoAgenda/f3191739-9044-46f9-9033-89db443abdf7/scratchpad/cleanroom
NT="--disallowed-tools Bash Read Write Edit Glob Grep WebSearch WebFetch Task NotebookEdit"
run(){
  i=$1; d=$C/run$i; mkdir -p $d; cd $d
  sid=$(timeout 900 claude -p $NT --model opus --output-format json < $R/prompts/s1.txt > $R/out/run${i}_s1.json 2>$R/out/run${i}_s1.err; \
        python3 -c "import json;print(json.load(open('$R/out/run${i}_s1.json'))['session_id'])" 2>/dev/null)
  echo "run$i session=$sid"
  [ -z "$sid" ] && { echo "run$i STAGE1 FAILED"; return; }
  timeout 900 claude -p --resume $sid $NT --model opus --output-format json < $R/prompts/s2.txt > $R/out/run${i}_s2.json 2>$R/out/run${i}_s2.err
  timeout 900 claude -p --resume $sid $NT --model opus --output-format json < $R/prompts/s3.txt > $R/out/run${i}_s3.json 2>$R/out/run${i}_s3.err
  echo "run$i done"
}
for i in 1 2 3; do run $i & done
wait
echo ALL_DONE
