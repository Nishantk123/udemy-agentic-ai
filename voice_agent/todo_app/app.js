document.addEventListener("DOMContentLoaded", function() {
    const input = document.getElementById("todo-input");
    const addBtn = document.getElementById("add-btn");
    const list = document.getElementById("todo-list");

    function addTodo() {
        const text = input.value.trim();
        if (!text) return;
        const li = document.createElement("li");
        li.textContent = text;
        const delBtn = document.createElement("button");
        delBtn.textContent = "Delete";
        delBtn.className = "delete-btn";
        delBtn.onclick = function() {
            list.removeChild(li);
        };
        li.appendChild(delBtn);
        list.appendChild(li);
        input.value = "";
        input.focus();
    }

    addBtn.addEventListener("click", addTodo);
    input.addEventListener("keypress", function(e) {
        if (e.key === "Enter") addTodo();
    });
});
