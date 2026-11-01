## Phase 3.1 — Task Group 2 Active Recall

### Question 1
Why does hyperparameter tuning create selection-induced optimism, and how does nested cross-validation separate the jobs of hyperparameter selection and performance evaluation? What roles do the inner grouped folds and outer grouped folds each play?

**Best sections to review: 2A — Why We Need Nested Cross-Validation, 2B — Why This Is Better Than Just `RandomizedSearchCV.best_score_`, and 2I — Why Two Levels of Grouping?**

*Hyperparameter tuning created selection-induced optimism because it's the result of trying many Extra Tree settings, choosing the best setting, and reporting that same CV score. This creates a situation where the score has participated in model selection, so it tends to be optimistic.*

*Nested cross-validation is able to separate the jobs of hyperparameter selection and performance evaluation by splitting outer cross-validation and inner cross-validation and using them for different parts of the training process. First, there is outer CV, which estimates the performance of the challenger. Second, inside each outer training set, there is inner CV. Inner CV is what chooses hyperparameters.*

*As for the roles the inner grouped folds and outer grouped folds play, the outer split asks how well the tuning procedure generalizes to engines that were never used for either fitting or tuning. Meanwhile, the inner split asks among these candidate hyperparameters, which configuration looks best using only the outer training engines.*

Inner CV chooses; outer CV judges.

Inner CV -> Which hyperparameters should I choose? 

Outer CV -> How well did that whole tuning procedure actually work on unseen engines? 

Once an evaluation result helps choose among configurations, it isn't fully independent evidence anymore.

### Question 2
What is `RandomizedSearchCV` doing in this experiment, why are we limiting it to six sampled Extra Trees configurations, and why does scikit-learn use `neg_root_mean_squared_error` instead of ordinary positive RMSE during model selection?

**Best sections to review: 2C — Keep the Search Small, 2D–2E — Search Dimensions, and 2H — Why `neg_root_mean_squared_error`?**

*In this experiment, `RandomizedSearchCV` samples a fixed number of parameter configurations using `n_iter`. From there, it evaluates them using its CV procedure and chooses the best configuration.*

*We are limiting our `RandomizedSearchCV` to six sampled Extra Trees because we want to keep the search small. Our goal is to show the results of real tuning wihtout spending an inordinate amount of time searching hyperparameters.*

*As for why scikit-learn uses `neg_root_mean_squared_error` instead of ordinary positive RMSE during model selection, the best possible RMSE is the one that is measured as being closest to zero. We want to account for cases where we might get values of -20 and -15 for RMSE, and know that the model with -15 RMSE is the better performer. This is done by returning `-search.best_score_` in our code.*

RMSE -> acutal error quantity

`neg_root_mean_squared_error` -> sklearn scoring representation of that quantity

### Question 3
Why should the inner best RMSE not be compared directly with the incumbent's performance, how should we interpret the outer pooled OOF RMSE and challenger-minus-incumbent delta, and why does even a tuned Extra Trees victory still not authorize replacing the served Random Forest?

**Best sections to review: 2L–2M — Delta and Inner-vs-Outer Evidence, 2O — The Decision Rule, and 2R — Preserve the Existing Incumbent**

*The inner best RMSE should not be compared directly with the incumbent's performance because the inner score is associated with tuning information. To get comparative performance evidence we should instead use the outer OOF results.*

*We should interpret the outer pooled OOF RMSE as comparative performance evidence. As for the challenger-minus-incumbent delta, this can go a few different ways as a result of us calculating it as `challenger RMSE - incumbent RMSE`. If it's negative, that means the challenger performed better; zero, then they are tied; positive, then the incumbent performed better.*

*A tuned Extra Trees victory still does not authorize replacing the served Random Forest because here we have only collected the data of an experiment. We need to enforce a boundary where one phase carries out an experiment and the next phase implements a decision making framework.*

inner score -> tuning evidence

outer OOF result -> comparative performance evidence

The challenger is modestly better under this nested evaluation, but it remains a challenger.

### Help Needed

* What is an outer versus inner cross-validation? 

* Can you talk me through drawing a sequence of pictures for understanding what's going on with nested cross-validation? I'm struggling with this conceptually. 

### Ideas to Retain

* Inner chooses; outer judges.

* Outer validation engines are excluded from both fitting and hyperparameter selection. 

* `RandomizedSearchCV.best_score_` describes the selection proces inside the training boundary; outer OOF performance is cleaner evidence about how that selection prodecure generalizes. 

* Negative RMSE is an sklearn convention; RMSE itself remains positive.