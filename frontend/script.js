
let chats =
    JSON.parse(
        localStorage.getItem("chats")
    ) || [];

let currentChat = null;

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
    if (currentChat) {
        const chat =
            chats.find(
                c => c.id === currentChat
            );

        if (chat) {

            chat.messages =
                chatBox.innerHTML;

            saveChats();
        }
    }

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
        const chat =
        chats.find(
            c => c.id === currentChat
        );
        
        if(chat){
            chat.messages =
            chatBox.innerHTML;
            if(chat.title === "New Chat"){
                chat.title =
                question.substring(
                    0,
                    20
                );
            }
            saveChats();
            renderChats();
        }

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

function newChat() {

    const id = Date.now();

    currentChat = id;

    chats.unshift({
        id: id,
        title: "New Chat",
        messages: ""
    });

    saveChats();

    renderChats();

    document.getElementById(
        "chatBox"
    ).innerHTML = `
        <div class="welcome">
            New Chat Started
        </div>
    `;
    chats[0].messages =
        document.getElementById(
            "chatBox"
        ).innerHTML;
    saveChats();
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

function saveChats() {

    localStorage.setItem(
        "chats",
        JSON.stringify(chats)
    );
}

function renderChats() {

    const history =
        document.getElementById(
            "chatHistory"
        );

    history.innerHTML = "";

    chats.forEach(chat => {

        const div =
            document.createElement("div");

        div.className = "doc-item";

        div.innerText = chat.title;

        div.onclick = () => {

            currentChat = chat.id;

            document.getElementById(
                "chatBox"
            ).innerHTML = chat.messages;
        };

        history.appendChild(div);
    });
}

renderChats();

if (chats.length > 0) {

    currentChat = chats[0].id;

    document.getElementById(
        "chatBox"
    ).innerHTML =
        chats[0].messages;
}