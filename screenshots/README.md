# Screenshots

This folder holds the screenshots used in the experiment report and README.

> Screenshot files are not yet included in this repository. Capture them from the running application
> and save them here using the names below. Do not add images that were not captured from the actual
> application.

---

## How to capture

1. Start the application:

   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```

2. Open <http://127.0.0.1:5000> in a browser and maximise the window (a width of about 1400 px looks best).
3. Use the browser's screenshot tool, Windows **Snipping Tool** (`Windows key + Shift + S`), or
   `Print Screen`. Save each image with the exact file name below.
4. Keep file sizes small (PNG, under about 500 KB each) so the repository stays lightweight.

---

## Required screenshots

| File name | What to capture | How to reproduce in the app |
|---|---|---|
| `01-extractor-complete.png` | Extractor tab with the sample paragraph loaded and all five fields extracted | Click **Load Sample Paragraph** → **Extract Information** |
| `02-missing-information.png` | Missing venue and speaker shown as `null` with the explanatory notes | Click **Load Missing-Info Example** → **Extract Information** |
| `03-test-suite.png` | Test Suite tab with 3 / 3 passed and the field-level tables | Open **Test Suite** → **Run All Tests** |
| `04-validation.png` | Schema validation detecting the deliberate errors | Open **Schema & Validation** → **Load invalid example** → **Validate JSON** |
| `05-report.png` | Experiment report page | Open the **Experiment Report** link |

Optional extras:

| File name | What to capture |
|---|---|
| `06-prompt-lab.png` | Prompt Lab tab showing the two prompts side by side |
| `07-learn-tab.png` | Learn tab with the explanations expanded |
| `08-mobile-view.png` | Narrow browser window showing the responsive layout |
| `09-pytest-run.png` | Terminal showing `107 passed` |

---

## Inserting screenshots into the documentation

### Markdown (README, docs)

```markdown
![Extractor with sample paragraph](screenshots/01-extractor-complete.png)
```

### Printed report

Insert the images under section 15 of the **Experiment Report** page, or paste them into your printed
report beneath the relevant section headings.
