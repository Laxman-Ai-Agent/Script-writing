# NVIDIA GR00T 2
- Unveiled Mon 2026-11-09 at Conference on Robot Learning (CoRL), Austin, Texas — https://thenextweb.com/news/nvidia-gr00t-2-robots-human-video-corl ; https://interestingengineering.com/ai-robotics/nvidia-groot-2-human-robot-skill-transfer — high
- Open "world action model": predicts future video and robot movement together — https://interestingengineering.com/ai-robotics/nvidia-groot-2-human-robot-skill-transfer ; https://research.nvidia.com/labs/gear/gr00t-2 — high
- Training data: 402,730 h first-person human video, 10,184 h handheld-gripper demos, 23,500 h robot teleoperation — https://interestingengineering.com/ai-robotics/nvidia-groot-2-human-robot-skill-transfer — medium (single source; TNW only says "including 100,000 h first-person footage")
- 100,000 h of human video (Human-1M dataset) released openly — https://thenextweb.com/news/nvidia-gr00t-2-robots-human-video-corl ; https://interestingengineering.com/ai-robotics/nvidia-groot-2-human-robot-skill-transfer — high (one search result says full dataset/weights arrive Dec 2026, unconfirmed)
- Zero-shot (no task-specific training) on 50 tasks: 40% average success — https://interestingengineering.com/ai-robotics/nvidia-groot-2-human-robot-skill-transfer ; https://research.nvidia.com/labs/gear/gr00t-2 — disputed (TNW words it as "40 of 50 tasks completed at least once"; NVIDIA page/IE say 40% average success. Use 40% average)
- 5 demos per task + fine-tune: 95% average success — https://thenextweb.com/news/nvidia-gr00t-2-robots-human-video-corl ; https://interestingengineering.com/ai-robotics/nvidia-groot-2-human-robot-skill-transfer — high
- Fine-tune ~30 min on a single RTX 5090, under 3 min of robot data per task — https://interestingengineering.com/ai-robotics/nvidia-groot-2-human-robot-skill-transfer — medium (single source)
- Five-fingered robot: funnel task learned from human-only demo, 65% of trials — https://interestingengineering.com/ai-robotics/nvidia-groot-2-human-robot-skill-transfer — medium (single source)
- Extra: 1 demo gives 71% average success — https://thenextweb.com/news/nvidia-gr00t-2-robots-human-video-corl ; https://emergent.sh/news/nvidia-gr00t-2-hits-71-one-shot-success — high
- Caveat: tasks were chosen from ones the model could already learn well (NVIDIA's own paper) — https://thenextweb.com/news/nvidia-gr00t-2-robots-human-video-corl — medium
- Caveat: all results are NVIDIA's own tests, no independent verification found — https://letsdatascience.com/news/nvidia-unveils-gr00t-2-and-isaac-lab-30-at-corl-867274ea ; search results — high
- Partners: Foxconn (AI server building), Siemens (factory work), Nexuni (laundry) testing; none has committed to production use — https://thenextweb.com/news/nvidia-gr00t-2-robots-human-video-corl — medium (IE names no partners)
- Turbo variant on Unitree G1 with Jetson Thor, 124 ms per prediction — https://interestingengineering.com/ai-robotics/nvidia-groot-2-human-robot-skill-transfer — medium
## Angle
- Core twist: a robot learns a skill by watching a human's first-person video (no robot trained on that task), and 5 demos + 30 min on a gaming GPU lift it from 40% to 95%.
- Misconception to correct: it is not factory-ready; 40% zero-shot, 95% only after fine-tuning, tasks hand-picked, NVIDIA's own tests, no confirmed production use.
