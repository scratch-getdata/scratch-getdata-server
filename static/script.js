var currentURL = window.location.href;

var errorMessage = "The (Javascripterror) you've requested does not exist.";

// Check if the URL contains specific patterns and modify the error message accordingly
if (currentURL.includes("/get/messages")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else if (currentURL.includes("/get/ocular/user/status")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else if (currentURL.includes("/get/user/country/") && currentURL.includes("user")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else if (currentURL.includes("/get/follower-count")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else if (currentURL.includes("/get/is_scratcher")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else if (currentURL.includes("/get/following-count")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else if (currentURL.includes("/get/wiwo")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else if (currentURL.includes("/get/aboutme")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else if (currentURL.includes("/get/project/creator")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "projectid");
} else if (currentURL.includes("/get/project/name")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "projectid");
} else if (currentURL.includes("/get/project/notes_and_credits")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "projectid");
} else if (currentURL.includes("/get/project/instructions")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "projectid");
} else if (currentURL.includes("/get/project/blocks")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "projectid");
} else if (currentURL.includes("/get/forum/title")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "forumid");
} else if (currentURL.includes("/get/forum/category")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "forumid");
} else if (currentURL.includes("/get/user/country")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else if (currentURL.includes("/get/ocular/user/status")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else if (currentURL.includes("/get/ocular/user/color")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else if (currentURL.includes("/get/ocular/user/updated_time")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else if (currentURL.includes("/get/user/profilepic")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user or size");
} else if (currentURL.includes("/get/studio/title/")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "studioid");
} else if (currentURL.includes("/get/studio")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "studioid");
} else if (currentURL.includes("/get/project")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "projectid");
} else if (currentURL.includes("/get/forum")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "forumid");
} else if (currentURL.includes("/get/studio/count_managers")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "studioid");
} else if (currentURL.includes("/get/user")) {
    errorMessage = errorMessage.replace("(Javascripterror)", "user");
} else {
    errorMessage = errorMessage.replace("(Javascripterror)", "page"); 
}

// Update the error message text in the HTML
window.onload = function() {
    var errorMessageElement = document.getElementById("error-message");
    errorMessageElement.innerText = errorMessage;
};
