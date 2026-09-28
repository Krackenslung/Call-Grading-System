# Evaluation: grader vs human labels

Labeled calls compared: **15** (model: claude-opus-5)

> n=15 is small: one disagreement moves exact agreement by 7 points. Read the per-call table, not just the rates.

## Per criterion

| Criterion | Exact | Within ±5 | Severe (0↔10) | Bias (grader − human) | Human dist. | Grader dist. | Weighted κ |
|---|---|---|---|---|---|---|---|
| C1 Greeting and Identification | 13/15 (87%) | 15/15 (100%) | 0 | +0.0 | 0:1 / 5:2 / 10:12 | 0:1 / 5:2 / 10:12 | 0.70 ⚠ unstable (human labels 80% one value) |
| C2 Needs Discovery | 7/15 (47%) | 15/15 (100%) | 0 | +1.3 | 0:1 / 5:8 / 10:6 | 0:2 / 5:2 / 10:11 | 0.27 |
| C3 Compliance and Disclosures | 13/15 (87%) | 13/15 (87%) | 2 | -1.3 | 0:0 / 5:1 / 10:14 | 0:2 / 5:1 / 10:12 | 0.29 ⚠ unstable (human labels 93% one value) |
| C4 Resolution and Next Steps | 14/15 (93%) | 15/15 (100%) | 0 | +0.3 | 0:2 / 5:5 / 10:8 | 0:2 / 5:4 / 10:9 | 0.91 |
| C5 Professionalism and Call Control | 12/15 (80%) | 15/15 (100%) | 0 | -0.3 | 0:1 / 5:4 / 10:10 | 0:1 / 5:5 / 10:9 | 0.66 |

## Total score (0–50)

- MAE: **4.0** points
- Bias (grader − human): **+0.0** points
- Exact total match: 5/15 (33%)

## Tune vs holdout (exact agreement over all criteria)

If the prompt was tuned by reading disagreements, only the tune calls were read; the holdout number is the one to trust.
- tune (C001, C002, C003, C004, C005, C006, C007): 30/35 (86%)
- holdout (C008, C009, C010, C011, C012, C013, C014, C015): 29/40 (72%)

## Confusion matrices

**C1 Greeting and Identification**

| human \ grader | 0 | 5 | 10 |
|---|---|---|---|
| **0** | 0 | 1 | 0 |
| **5** | 1 | 1 | 0 |
| **10** | 0 | 0 | 12 |

**C2 Needs Discovery**

| human \ grader | 0 | 5 | 10 |
|---|---|---|---|
| **0** | 1 | 0 | 0 |
| **5** | 1 | 1 | 6 |
| **10** | 0 | 1 | 5 |

**C3 Compliance and Disclosures**

| human \ grader | 0 | 5 | 10 |
|---|---|---|---|
| **0** | 0 | 0 | 0 |
| **5** | 0 | 1 | 0 |
| **10** | 2 | 0 | 12 |

**C4 Resolution and Next Steps**

| human \ grader | 0 | 5 | 10 |
|---|---|---|---|
| **0** | 2 | 0 | 0 |
| **5** | 0 | 4 | 1 |
| **10** | 0 | 0 | 8 |

**C5 Professionalism and Call Control**

| human \ grader | 0 | 5 | 10 |
|---|---|---|---|
| **0** | 0 | 1 | 0 |
| **5** | 1 | 3 | 0 |
| **10** | 0 | 1 | 9 |

## Disagreements (16)

| Call | Crit | Human | Grader | Grader justification | Evidence | Quote found? |
|---|---|---|---|---|---|---|
| C007 | C3 **SEVERE** | 10 | 0 | No recording disclosure appears anywhere in the call, and the agent additionally presents the pre-underwriting price as essentially final, both of which force a 0. | El monto queda sujeto a la revisión de suscripción, pero es prácticamente el final. | yes |
| C011 | C3 **SEVERE** | 10 | 0 | Although the recording disclosure was delivered properly at the start, the agent made a prohibited guarantee about the service outcome of the add-on coverage, which is an automatic 0 under the gate rule. | la nuestra tiene tiempo de respuesta garantizado | yes |
| C002 | C2 | 5 | 10 | The agent gathered identifying information and probed the billing issue, confirming the customer's account and the specific charge before acting, appropriate to the service nature of the call. | Can I have your policy number or the phone number on the account? | yes |
| C003 | C2 | 5 | 10 | Before proposing anything, the agent established the vehicle, its age/value, current premium, the competitor benchmark, the budget pressure, and the must-keep coverage, then explicitly confirmed her understanding. | Muy bien, entonces: Jetta 2018, cobertura amplia con cristales, y buscamos bajar de mil quinientos... | yes |
| C004 | C5 | 5 | 0 | The agent repeatedly talked over the customer, dismissed her stated needs, and lost the call entirely by steamrolling her request. | See, that's what everyone says, and then something happens and they wish they had the full package. Trust me, I've been doing this a while. | yes |
| C005 | C2 | 5 | 10 | The agent gathered the policy number, confirmed the renewal notice the customer received, identified the specific vehicle and existing deductible, and confirmed understanding before proposing any change. | ¿Me da su número de póliza por favor? | yes |
| C008 | C2 | 5 | 10 | Agent asked targeted questions (existing claim, claim number) and demonstrated a complete, confirmed understanding of the issue before handing off, as shown by her accurate recap. | te paso al señor con el siniestro SIN-4521, choque reportado la semana pasada, el taller le dice tres semanas por una pieza pero su ajustador le había dicho dos, necesita que le confirmen el tiempo real | yes |
| C009 | C1 | 5 | 0 | The agent gives a casual greeting and his first name but never states the company name anywhere, which the rubric defines as a 0-level failure. | Thanks for calling, this is Tony. Oh, this call may be recorded, by the way. What's up? | yes |
| C009 | C2 | 5 | 0 | There is no discovery at all — the agent asks no questions about the driver, vehicle, or coverage needs, and in fact loses track of why the customer called. | so what was it you were calling about again? | yes |
| C009 | C5 | 0 | 5 | The agent stays courteous but repeatedly derails with irrelevant anecdotes, dead air, and loses the thread of the customer's request. | man, it's really coming down out there today, is it raining where you are? | yes |
| C010 | C2 | 5 | 10 | For a simple document request the agent gathered the needed information (policy number, confirmed delivery email) and confirmed understanding before acting, which is full discovery for this call's scope. | ¿Me confirma su número de póliza?... ¿Se la mando al correo que tenemos registrado, el de hotmail? | yes |
| C011 | C2 | 10 | 5 | The agent verified the policy, vehicle and use before processing the payment change, but then launched into a roadside-assistance pitch without any discovery and pressed on after the customer explained he already had that benefit. | Antes de que se vaya, señor Ibarra, veo que su póliza no trae asistencia vial. Por ochenta pesitos al mes le agregamos grúa, paso de corriente, cambio de llanta. ¿Se la agrego? | yes |
| C011 | C4 | 5 | 10 | The customer's reason for calling was fully resolved on the call, with the new payment method registered, the next charge date confirmed, and a same-day email confirmation promised. | El cambio de forma de pago ya quedó hecho, le llega la confirmación por correo hoy mismo. | yes |
| C012 | C1 | 0 | 5 | The greeting includes the company name but is cut off by the customer before the agent states their own name, leaving identification incomplete. | Gracias por llamar a Seguros Confianza, le atien... | yes |
| C014 | C2 | 5 | 10 | The agent probes vehicle, ownership status, primary driver, usage, coverage level, deadline, and add-ons, then recaps to confirm understanding before proposing anything. | Corolla 2024, conductora principal su esposa, uso diario al trabajo, cobertura amplia. | yes |
| C014 | C5 | 10 | 5 | The agent is courteous and controls the call well but loses the thread at the close by confusing the vehicle and the agreed deadline, leaving the customer hesitant. | Eh... bueno, sí, gracias. Ahí espero la llamada. | yes |

## Evidence check (all graded calls)

Quotes that do not appear verbatim in the transcript: **0**

## Grader mean score: labeled vs unlabeled calls

A large gap means the unlabeled calls differ from the calibration set, so calibration agreement may not carry over.

| Criterion | C001–C015 | C016–C030 |
|---|---|---|
| C1 | 8.7 | 9.0 |
| C2 | 8.0 | 8.0 |
| C3 | 8.3 | 7.7 |
| C4 | 7.3 | 9.0 |
| C5 | 7.7 | 8.0 |
