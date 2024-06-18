let loginForm = document.getElementById("newUserForm");

loginForm.addEventListener("submit", (e) => {
  e.preventDefault();

  let username = document.getElementById("username");
  let password = document.getElementById("pass");

  const apiUrl = `/newUser/${username.value}/${password.value}`;
    fetch(apiUrl)
        .then(response => response.json())
        .then((data)=>{
            if (data['status'] == "success")
            {
                window.location.href = `/board?username=${username.value}`;
            }
            else
            {
                var element = document.getElementById("error");
                element.classList.add("error-style");
                var element = document.getElementById("username-box");
                element.classList.add("username-style");
                var element = document.getElementById("pass-box");
                element.classList.add("pass-style");
                var element = document.getElementById("button");
                element.classList.add("button-style");
            }
        })
});