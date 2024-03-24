stories = [["There was a small dog. He ate food.", "He all of a sudden felt sick", "But he went to the vet."], 
["Anna watched her mom come home.", "She said lets go eat"]]

let likes = []
let seen = []
let current_story_id = -1

currPage = 0

let current_story = []
const storyElement = document.querySelector(".story");
const circles = document.querySelector('.circles')


function splitByEveryNthNewLine(text, n) {
    let parts = [];
    let lastIndex = 0;
    let newlineCount = 0;

    for (let i = 0; i < text.length; i++) {
        if (text[i] === "\n") {
            newlineCount++;
            if (newlineCount === n) {
                // Include the part up to the current position, excluding the current newline
                parts.push(text.substring(lastIndex, i));
                lastIndex = i + 1; // Start after the current newline
                newlineCount = 0; // Reset counter
            }
        }
    }

    // Add the last part of the text if there's any left
    if (lastIndex < text.length) {
        parts.push(text.substring(lastIndex));
    }

    return parts;
}

async function loadStoryAndUpdateUI() {
    try {
        const data = await getStory();
        current_story = splitByEveryNthNewLine(data['content'], 20).filter(line => line !== "");
        storyElement.innerHTML = current_story[currPage];
        seen.push(data['id'])
        console.log("seen", seen)
        console.log("likes", likes)
        current_story_id = data['id']
        circles.innerHTML = ""
        for (let i = 0; i < current_story.length; i++) {
            if (i === currPage) {
                circles.innerHTML += "&#9673;"
            }
            else {
                circles.innerHTML += "&#9711;"
            }
        }
        // Assuming the JSON has a 'content' key
    } catch (error) {
        console.error("Failed to load story:", error);
        // Optionally handle the error, e.g., show an error message in the UI
    }
}

loadStoryAndUpdateUI();

function getStory() {
    return fetch("http://127.0.0.1:5000/get-text", {
        method: "POST",
        body: JSON.stringify({
            seen: seen,
            likes: likes
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .catch(error => {
        console.error('There was a problem with your fetch operation:', error);
        throw error; // Rethrow after logging to allow caller to handle
    });
}


document.addEventListener("keydown", function(e) {

    if (e.keyCode == 68 && currPage < current_story.length - 1) {
        currPage++;
        storyElement.innerHTML = current_story[currPage];
    }
    else if ( e.keyCode === 65 && currPage > 0) {
        currPage--;
        storyElement.innerHTML = current_story[currPage];
    }
    else if (e.keyCode === 83) {
           loadStoryAndUpdateUI();
    }
    else if (e.keyCode === 76) {
        if (!likes.includes(current_story_id)) {
            likes.push(current_story_id)
        }
        console.log("likes", likes)
    }
    circles.innerHTML = ""
    for (let i = 0; i < current_story.length; i++) {
        if (i === currPage) {
            circles.innerHTML += "&#9673;"
        }
        else {
            circles.innerHTML += "&#9711;"
        }
    }
})
