# quiz score calculator
from flask import request


def score_calc(chap):
        score = 0
        count = 0
        for q in chap.ques:
            ans = request.form.get(str(q.id))
            # print(q.correct)
            # print(q.id)
            count += 1
            # print(count)
            if ans == q.correct:
                score += 1
                # print(score)
        total = (score/count)*100
        # print(total)
        return total