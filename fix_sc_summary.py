"""Patch the Results Summary cell in REG Society & Culture.ipynb."""
import json, re

NB = r'C:\Users\neddp\ECC3479-Project-JRGS\docs\Regression Analysis\REG Society & Culture.ipynb'

SUMMARY = r"""## Results Summary

### Model specification

$$\log(E_{ct}) = \beta_0 + \beta_1 \cdot \text{Treated}_c + \beta_2 \cdot \text{DID}_{ct} + \sum_{t=2020}^{2024} \gamma_t \cdot \mathbf{1}_{[\text{year}=t]} + \varepsilon_{ct}$$

| Term | Variable | Definition |
|------|----------|------------|
| $\log(E_{ct})$ | Outcome | Log enrolments for country $c$ in year $t$ |
| $\beta_0$ | Intercept | UK baseline (2019) |
| $\beta_1 \cdot \text{Treated}_c$ | Country FE | $\text{Treated}_c = 1$ if AUS, $0$ if UK |
| $\text{Post}_t$ | --- | $= 1$ if $t \geq 2021$, else $0$ |
| $\text{DID}_{ct}$ | DiD term | $= \text{Treated}_c \times \text{Post}_t$ |
| $\beta_2$ | **JRG effect** | DiD estimate --- the coefficient of interest |
| $\gamma_t$ | Year FEs | Common time trend absorbed by year dummies (2020--2024) |
| $\varepsilon_{ct}$ | Error | HC3 heteroscedasticity-robust standard errors |

**Implemented in statsmodels as:**
```python
formula = "log_enrollments ~ treated + did + C(year)"
model   = smf.ols(formula, data=panel).fit(cov_type="HC3")
```

**Panel:** N = 12 (2 countries × 6 years, 2019--2024) | df = 4

| **Cell** | **Result** |
|----------|------------|
| **Main DiD** | $\hat{\beta} = -0.0319$, SE = 0.037, p = 0.389, 95% CI [$-$0.105, +0.041], approx. **−3.1%** relative to UK trend |
| **PanelOLS cross-check** | Estimates match exactly |
| **COVID sensitivity** | Full: −3.1% (p=0.389); dropping years produces degenerate SEs (2-country panel issue). Sign consistent (negative) across all variants |
| **Event study** | Pre-trend: +3.3% (2019). Post-JRG: +1.3% (2021), −3.0% (2022), −3.4% (2023), −1.0% (2024) |
| **Placebo** | fake\_post coef = −0.006, p = 0.854 --- no significant pre-trend break in AUS-only data |
| **Level spec** | $\hat{\beta} = -40{,}980$ students, p = 0.364, 95% CI [$-$129,477, +47,517] --- directionally consistent, not significant |

**Substantive finding:** Post-JRG, AUS S&C enrolments were approximately **−3.1% lower**
than the UK trend would predict ($\hat{\beta} = -0.0319$, p = 0.389, not significant, df = 4).
This is a null result --- no statistically detectable JRG effect on S&C enrolments at conventional
significance levels.

The event study reveals a nuanced pattern: 2021 showed a slight AUS outperformance (+1.3%),
likely reflecting a lagged COVID-rebound effect, followed by UK outperformance in 2022--2023
(−3.0%, −3.4%) before convergence in 2024 (−1.0%). The overall post-period average is
marginally negative but insignificant. The single pre-treatment point (+3.3% in 2019) suggests
AUS was growing slightly faster than UK before JRG, meaning the post-JRG negative gap is
slightly understated relative to a counterfactual with pre-existing AUS-favourable trend.

Society & Culture received the **largest student fee increase** of any discipline (+65.1%),
with Commonwealth funding falling 34.2%. Despite this strong discouragement signal, no
statistically significant reduction in AUS enrolments relative to the UK benchmark is detected.
This may reflect inelastic demand for S&C degrees (psychology, law, social sciences) or
compositional effects within the broad category masking heterogeneous sub-field responses.

The level specification (--40,980 students/year, p = 0.364) is directionally consistent with
the log-linear result and supports the null finding at conventional significance thresholds.

> **Data limitation:** UK panel restricted to 2019--2024 (N = 12, df = 4) due to irreconcilable
> JACS→CAH taxonomy break in 2019/20. Pre-2019 UK data at key = 9 contains only "04 Veterinary
> science" (~6--8K), a clear misassignment. Even reconstructing correct JACS subjects yields
> ~554--565K, leaving an irreconcilable ~167K gap vs post-2019 CAH totals (~731--788K) driven by
> Psychology having no JACS equivalent. Only 1 pre-treatment observation (2019) is available
> for the event study, preventing a formal parallel-trends test.
"""

with open(NB, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell 21 is the Results Summary
c = nb['cells'][21]
assert c['cell_type'] == 'markdown', f'Cell 21 is {c["cell_type"]}, expected markdown'
c['source'] = SUMMARY
# Ensure no code-specific keys on markdown cells
c.pop('outputs', None)
c.pop('execution_count', None)

with open(NB, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Results Summary patched successfully.')
