window.addEventListener('load', () => {
      // Get user's location
      if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(position => {
              const { latitude, longitude } = position.coords;
              
              // Use OpenWeatherMap API
              const apiKey = '98814bbdea572dfeaa0582d0e5bdb25d'; // Replace with your OpenWeatherMap API key
              const apiEndpoint = `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${apiKey}&units=metric`;

              // Fetch weather data
              fetch(apiEndpoint)
                  .then(response => response.json())
                  .then(data => {
                      // console.log(data)
                      const locationElement = document.getElementById('location');
                      const temperatureElement = document.getElementById('temperature');
                      // const weatherIconElement = document.getElementById('weather-icon');
                      const descriptionElement = document.getElementById('description');
                      const humidityElement = document.getElementById('humidity');
                      const windElement = document.getElementById('wind');

                      locationElement.textContent = `${data.name}, ${data.sys.country}`;
                      temperatureElement.textContent = `${data.main.temp}°C`;
                      windElement.textContent = `Wind: ${data.wind.speed} km/h`;
                      humidityElement.textContent = ` Humidity: ${data.main.humidity}%`;
                      // weatherIconElement.src = `https://openweathermap.org/img/wn/${data.weather[0].icon}.png`;
                      // descriptionElement.textContent = `${data.weather[0].description}`;
                  })
                  .catch(error => console.error('Error fetching weather data:', error));
          });
      } else {
          console.error('Geolocation is not supported by this browser.');
      }

      window.addEventListener('scroll',()=>{
        var scroll = window.scrollY;
          var blackElement = document.querySelector("#navbar");
          var weatherCont = document.querySelector(".weather-container");
        if (scroll > 10) {
            blackElement.style.background = "#cbd5c0";
            // blackElement.style.top = "0px";
            blackElement.style.transition = "all 1.2s";
        }
        
        else{
            blackElement.style.background = "transparent";
            // blackElement.style.top = "15px";
            blackElement.style.transition = "all 1.2s";
    
        }
      });
      
      
  });

  function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
  }
  
  function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
  }

  function displayFlex(){
    document.querySelector(".transparent-back").classList.add('.flex');
  }

 


  

