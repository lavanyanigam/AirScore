from flask import Flask, render_template, request
import requests

app=Flask(__name__)
api_key="67e2be7b1958936d46c2b55b8e0db7bd5e959fc0"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/aqi", methods=["POST"])
def get_aqi():
    city=request.form['city']
    url= f"https://api.waqi.info/feed/{city}/?token={api_key}"
    response = requests.get(url).json()

    if response.get("status") != "ok":
        return render_template('index.html', error="City not found.")
    
    data = response["data"]

    aqi_data = {
        "city": data["city"]["name"],
        "aqi": data["aqi"],
        "pm25": data["iaqi"].get("pm25", {}).get("v", "N/A"),
        "pm10": data["iaqi"].get("pm10", {}).get("v", "N/A"),
    }
    return render_template('aqi.html', aqi_data=aqi_data)

@app.route("/airscore")
def airscore():

    return render_template("airscore.html")

@app.route("/aqiscore", methods=["POST"])
def aqi_score():
    
    city = request.form.get("city")
    workout_duration = request.form.get("workout_duration")
    intensity = request.form.get("intensity")
    location = request.form.get("location")
    if not city or not workout_duration or not intensity or not location:
        return render_template("airscore.html", error="Please fill all fields.")

    try:
        workout_duration = int(workout_duration)
    except ValueError:
        return render_template("airscore.html", error="Workout duration must be a number.")

    url = f"https://api.waqi.info/feed/{city}/?token={api_key}"
    response = requests.get(url).json()

    if response.get("status") != "ok":
        return render_template("airscore.html", error="City not found.")

    aqi = response["data"]["aqi"]
    if aqi<100: 
        risk_score = aqi * 0.3 
    else: 
        risk_score = aqi * 0.7

    if intensity == "medium" and aqi > 100:
        risk_score += 15
    elif intensity == "hard" and aqi > 100:
        risk_score += 30

    if location == "outdoor" and aqi > 100:
        risk_score += 25

    if aqi > 100:
        risk_score += workout_duration * 0.6
    else:
        risk_score += workout_duration * 0.3

    risk_score = round(risk_score, 1)

    benefit_score = workout_duration * 1.1

    if intensity == "easy":
        benefit_score += 10
    elif intensity == "medium":
        benefit_score += 25
    elif intensity == "hard":
        benefit_score += 50

    if location == "indoor":
        benefit_score += 10

    benefit_score = round(benefit_score, 1)


    net_score = round(benefit_score - risk_score, 1)

    if net_score > 30:
        verdict = "Highly Beneficial"
        color = "green"
    elif net_score > 0:
        verdict = "Moderately Beneficial"
        color = "orange"
    else:
        verdict = "More Harm Than Benefit"
        color = "red"

    return render_template(
        "aqiscore.html",
        city=city,
        aqi=aqi,
        risk_score=risk_score,
        benefit_score=benefit_score,
        net_score=net_score,
        verdict=verdict,
        color=color,
        intensity=intensity,
        location=location,
        workout_duration=workout_duration
    )



@app.route("/personalizedworkout")
def personalizedworkout():
    return render_template("personalizedworkout.html")


if __name__=="__main__":
    app.run(debug=True, port=5001)