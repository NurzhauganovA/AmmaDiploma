function nextQuestion(currentQuestionId) {

    let options = document.getElementsByName("question" + currentQuestionId);
    let selectedOption = null;
    for (let i = 0; i < options.length; i++) {
        if (options[i].checked) {
            selectedOption = options[i].value;
            break;
        }
    }
    if (!selectedOption) {
        alert("Please select an option.");
        return;
    }

    const listQuestions = [
        // {% for q in questions %}
        //     {
        //         questionId: 'question{{ q.id }}'
        //     },
        // {% endfor %}
    ]

    for (let i = 0; i < listQuestions.length; i++) {
        if (listQuestions[i].questionId === `question${currentQuestionId}`) {
            document.getElementById(listQuestions[i].questionId).style.display = 'none';
            if (i < listQuestions.length - 1) {
                document.getElementById(listQuestions[i + 1].questionId).style.display = 'block';
            } else {
                document.querySelector('form').submit();
            }
            break;
        }
    }
}