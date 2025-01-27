import datetime as dt
from datetime import datetime

from flask import flash, jsonify, redirect, render_template, request, url_for

from app import database
from app.forms import AddUser
from app.models import Claim, Service, User

from . import home as home_blueprint


@home_blueprint.route("/all/users", methods=["GET"])
def all_users():
    """
    List all Users
    """
    data = User.query.all()
    return render_template("home/home.html", users=data, title="Users")


@home_blueprint.route("/user/<int:id>", methods=["GET", "POST"])
def view_user(id):
    """
    A route that allows claim officer fillout a form for a particular user
    """
    user_data = User.query.get(id)
    return render_template("home/user_data.html", user_data=user_data)


@home_blueprint.route("/user/<int:id>/edit", methods=["GET", "POST"])
def edit_user(id):
    """
    A route for editing a user record
    """
    form = AddUser()

    user_data = User.query.get(id)

    if request.method == "POST":
        name = request.form.get("name")
        gender = request.form.get("gender")
        salary = request.form.get("salary")
        date_of_birth = request.form.get("date_of_birth")

        dt_obj = datetime.strptime(date_of_birth, "%Y-%m-%d").strftime("%d-%m-%Y")

        if form.validate_on_submit():
            user_data.name = name
            user_data.gender = gender
            user_data.salary = salary
            user_data.date_of_birth = datetime.strptime(dt_obj, "%d-%m-%Y")

            database.session.commit()

            flash("User updated successfully.", "success")
            return redirect(url_for("home.edit_user", id=user_data.id))

    return render_template("home/edit_user.html", user_data=user_data, form=form)


@home_blueprint.route("users/add", methods=["GET", "POST"])
def add_user():
    """
    A route for adding users

    """
    form = AddUser()

    if request.method == "POST":
        name = request.form.get("name")
        gender = request.form.get("gender")
        salary = request.form.get("salary")
        date_of_birth = request.form.get("date_of_birth")

        dt_obj = datetime.strptime(date_of_birth, "%Y-%m-%d").strftime("%d-%m-%Y")

        if form.validate_on_submit():
            new_user = User(
                name=name,
                gender=gender,
                salary=salary,
                date_of_birth=datetime.strptime(dt_obj, "%d-%m-%Y"),
            )
            database.session.add(new_user)
            database.session.commit()

            flash("User created successfully.", "success")
            return redirect(url_for("home.all_users"))

        flash("You entered and invalid form data", "danger")
        return render_template("home/create_user.html", form=form)
    else:
        return render_template("home/create_user.html", form=form)


@home_blueprint.route("/user/<int:id>/delete", methods=["POST"])
def delete_user(id):
    """
    A route for deleting a user
    """
    user_data = User.query.get(id)
    if user_data:
        # Delete all associated claims and services
        for claim in user_data.claim:
            for service in claim.service:
                database.session.delete(service)
            database.session.delete(claim)
        database.session.delete(user_data)
        database.session.commit()
        flash(
            "User and all associated claims and services deleted successfully.",
            "success",
        )
    else:
        flash("User not found.", "danger")
    return redirect(url_for("home.all_users"))


@home_blueprint.route("claim", methods=["GET"])
def claim():
    """
    List all Claims
    """
    all_claims = Claim.query.all()
    return render_template("home/claim.html", claims=all_claims, title="Claims")


@home_blueprint.route("create_claim", methods=["GET", "POST"])
def create_claim():
    """
    A route for a claim officer to make/create a claim
    """

    if request.method == "POST":
        # Get the form field values for claim model insertion

        user = request.form.get("user")
        diagnosis = request.form.get("diagnosis")
        hmo = request.form.get("hmo")
        age = request.form.get("age")

        total_cost = request.form.get("total_cost")
        service_charge = request.form.get("service_charge")
        final_cost = request.form.get("final_cost")

        user = User.query.filter_by(name=user).first()

        new_claim = Claim(
            user_id=user.id,
            diagnosis=diagnosis,
            hmo=hmo,
            age=age,
            is_male=user.gender == "male",
            service_charge=service_charge,
            total_cost=total_cost,
            final_cost=final_cost,
        )
        database.session.add(new_claim)
        database.session.commit()

        # Get the form field values for service model insertion
        service_name = request.form.getlist("service_name")
        service_type = request.form.getlist("type")
        provider_name = request.form.getlist("provider_name")
        source = request.form.getlist("source")
        cost_of_service = request.form.getlist("cost_of_service")

        dates = request.form.getlist("service_date")

        # Format dates
        service_date = []
        for d in dates:
            service_date.append(datetime.strptime(d, "%Y-%m-%d").strftime("%d-%m-%Y"))

        # Get the above claim as foreign key for services
        claim = Claim.query.order_by(Claim.id.desc()).first()

        # Loop to enter possible list of services
        for i in range(len(service_name)):
            new_service = Service(
                claim_id=claim.id,
                service_date=datetime.strptime(service_date[i], "%d-%m-%Y"),
                service_name=service_name[i],
                type=service_type[i],
                provider_name=provider_name[i],
                source=source[i],
                cost_of_service=cost_of_service[i],
            )
            database.session.add(new_service)
            database.session.commit()

        flash("Claim created successfully.", "success")
        return redirect(url_for("home.claim"))
    else:
        data = User.query.with_entities(User.name).all()
        return render_template("home/create_claim.html", all_users=data)


@home_blueprint.route("create_claim/patient_data/", methods=["POST"])
def user_gender_age():
    """
    A route to get a user's birthdate
    and calculate his age
    """
    if request.method == "POST":
        user = User.query.filter_by(name=request.form.get("patient").strip()).first()
        age = dt.date.today().year - user.date_of_birth.year

        return jsonify({"age": age, "gender": user.gender})
    return jsonify({"message": "Please use POST request"})
