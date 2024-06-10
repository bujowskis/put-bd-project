
// generic request, given only thing that changes is action
const sendRequest = (action, resultElementId) => {
    fetch('/process', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            'action': action,
            'isbn': document.getElementById("isbn").value,
            'title': document.getElementById("title").value,
            'author': document.getElementById("author").value,
            'yearOfPublication': document.getElementById("yearOfPublication").value,
            'publisher': document.getElementById("publisher").value,
            'borrowerId': document.getElementById("borrowerId").value
        })
    })
        .then(response => response.json())
        .then(data => document.getElementById(resultElementId).innerHTML = data.result);
};

// click event listeners on action buttons to send process requests
document.getElementById("add").addEventListener(
    "click", () => sendRequest('add', 'result'));
document.getElementById("remove").addEventListener(
    "click", () => sendRequest('remove', 'result'));
document.getElementById("info").addEventListener(
    "click", () => sendRequest('info', 'result'));
document.getElementById("borrow").addEventListener(
    "click", () => sendRequest('borrow', 'result'));
document.getElementById("return").addEventListener(
    "click", () => sendRequest('return', 'result'));
document.getElementById("list").addEventListener(
    // apply on books, to make it possible to view books and work on them at the same time
    "click", () => sendRequest('list', 'books'));
