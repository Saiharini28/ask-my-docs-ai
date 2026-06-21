const API_URL = "http://127.0.0.1:5000";

async function uploadPDF() {

    const fileInput = document.getElementById("pdfFile");

    if (!fileInput.files.length) {
        alert("Select a PDF first");
        return;
    }

    const formData = new FormData();

    formData.append(
        "file",
        fileInput.files[0]
    );

    try {

        const response = await fetch(
            `${API_URL}/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        alert(data.message);

    } catch (error) {

        console.error(error);

        alert("Upload failed");
    }
}

async function sendMessage() {

    const questionInput =
        document.getElementById("question");

    const question =
        questionInput.value.trim();

    if (!question) return;

    const chatBox =
        document.getElementById("chatBox");

    chatBox.innerHTML += `
        <div class="message user">
            ${question}
        </div>
    `;

    questionInput.value = "";

    try {

        const response = await fetch(
            `${API_URL}/chat`,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    message: question
                })
            }
        );

        const data =
            await response.json();

        chatBox.innerHTML += `
            <div class="message bot">
                ${data.answer}
            </div>
        `;

        chatBox.scrollTop =
            chatBox.scrollHeight;

    } catch (error) {

        console.error(error);

        chatBox.innerHTML += `
            <div class="message bot">
                Error connecting to server
            </div>
        `;
    }
}

document
.getElementById("question")
.addEventListener(
    "keypress",
    function(event){

        if(event.key === "Enter"){
            sendMessage();
        }

    }
);

function newChat(){

    document.getElementById(
        "chatBox"
    ).innerHTML = `
        <div class="welcome">
            New Chat Started
        </div>
    `;

}

async function loadDocuments() {

    const response = await fetch(
        "http://127.0.0.1:5000/documents"
    );

    const docs = await response.json();

    const sidebar = document.querySelector(".sidebar");

    docs.forEach(doc => {

        const item = document.createElement("div");

        item.innerText = "📄 " + doc;

        item.classList.add("doc-item");

        sidebar.appendChild(item);
    });
}

loadDocuments();