function nextStep(step){

for(let i=1;i<=5;i++){
document.getElementById("step"+i).style.display="none"
}

document.getElementById("step"+step).style.display="block"

}


function submitSetup(){

let data={

location:{
latitude:document.getElementById("latitude").value === 'custom' ? document.getElementById("latitude-custom").value : document.getElementById("latitude").value,
longitude:document.getElementById("longitude").value === 'custom' ? document.getElementById("longitude-custom").value : document.getElementById("longitude").value,
altitude:document.getElementById("altitude").value === 'custom' ? document.getElementById("altitude-custom").value : document.getElementById("altitude").value,
installation_type:document.getElementById("installation_type").value,
terrain_type:document.getElementById("terrain_type").value
},

solar:{
panel_model:document.getElementById("panel_model").value,
panel_count:document.getElementById("panel_count").value,
panel_power:document.getElementById("panel_power").value,
panel_efficiency:document.getElementById("panel_efficiency").value,
tilt_angle:document.getElementById("tilt_angle").value,
azimuth_angle:document.getElementById("azimuth_angle").value,
installation_type:document.getElementById("solar_installation").value,
inverter_efficiency:document.getElementById("inverter_efficiency").value,
system_loss:document.getElementById("system_loss").value,
shading_factor:document.getElementById("shading_factor").value
},

wind:{
turbine_model:document.getElementById("turbine_model").value,
turbine_count:document.getElementById("turbine_count").value,
rated_power:document.getElementById("rated_power").value,
cut_in_speed:document.getElementById("cut_in_speed").value,
cut_out_speed:document.getElementById("cut_out_speed").value,
hub_height:document.getElementById("hub_height").value,
rotor_diameter:document.getElementById("rotor_diameter").value,
turbine_efficiency:document.getElementById("turbine_efficiency").value
},

battery:{
battery_capacity:document.getElementById("battery_capacity").value,
battery_voltage:document.getElementById("battery_voltage").value,
charge_efficiency:document.getElementById("charge_efficiency").value,
discharge_efficiency:document.getElementById("discharge_efficiency").value,
max_discharge_rate:document.getElementById("max_discharge_rate").value
},

consumption:{
daily_energy_usage:document.getElementById("daily_energy_usage").value,
peak_load:document.getElementById("peak_load").value,
critical_load:document.getElementById("critical_load").value,
load_profile_type:document.getElementById("load_profile_type").value
}

}

// Store setup data in session storage
sessionStorage.setItem('setupData', JSON.stringify(data));

// Send data to backend
fetch('/submit_setup', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(result => {
    console.log('Setup data submitted:', result);
    // Redirect to AI page
    window.location.href = "ai.html";
})
.catch(error => {
    console.error('Error submitting setup:', error);
    // Still redirect to AI page even if submission fails
    window.location.href = "ai.html";
});

}
function login() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // Simple validation
    if (name && email && password) {
        // Send login request to backend
        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                // Store user info in session storage
                sessionStorage.setItem('userName', name);
                sessionStorage.setItem('userEmail', email);
                sessionStorage.setItem('userId', result.user.id);
                
                // Redirect to setup page
                window.location.href = "setup.html";
            } else {
                alert("Login failed: " + (result.error || "Unknown error"));
            }
        })
        .catch(error => {
            console.error('Login error:', error);
            alert("Login failed. Please try again.");
        });
    } else {
        alert("Please fill in all fields.");
    }
}
