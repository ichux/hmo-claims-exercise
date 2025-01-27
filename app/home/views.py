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
    user_data = User.query.get_or_404(id)
    return render_template("home/user_data.html", user_data=user_data)


@home_blueprint.route("/user/<int:id>/edit", methods=["GET", "POST"])
def edit_user(id):
    """
    A route for editing a user record
    """
    user_data = User.query.get_or_404(id)
    form = AddUser(obj=user_data)

    if form.validate_on_submit():
        form.populate_obj(user_data)
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

    if form.validate_on_submit():
        new_user = User()
        form.populate_obj(new_user)
        database.session.add(new_user)
        database.session.commit()
        flash("User created successfully.", "success")
        return redirect(url_for("home.all_users"))

    return render_template("home/create_user.html", form=form)


@home_blueprint.route("/user/<int:id>/delete", methods=["POST"])
def delete_user(id):
    """
    A route for deleting a user
    """
    user_data = User.query.get_or_404(id)
    for claim in user_data.claim:
        for service in claim.service:
            database.session.delete(service)
        database.session.delete(claim)
    database.session.delete(user_data)
    database.session.commit()
    flash(
        "User and all associated claims and services deleted successfully.", "success"
    )
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
        try:
            claim_data = {
                "user": request.form.get("user"),
                "diagnosis": request.form.get("diagnosis"),
                "hmo": request.form.get("hmo"),
                "age": request.form.get("age"),
                "service_charge": request.form.get("service_charge"),
                "total_cost": request.form.get("total_cost"),
                "final_cost": request.form.get("final_cost"),
            }

            user = User.query.filter_by(name=claim_data["user"]).first()

            new_claim = Claim(
                user_id=user.id,
                is_male=user.gender == "male",
                diagnosis=claim_data["diagnosis"],
                hmo=claim_data["hmo"],
                age=claim_data["age"],
                service_charge=claim_data["service_charge"],
                total_cost=claim_data["total_cost"],
                final_cost=claim_data["final_cost"],
            )

            database.session.add(new_claim)
            database.session.commit()

            service_dates = request.form.getlist("service_date")

            service_data = {
                "service_name": request.form.getlist("service_name"),
                "type": request.form.getlist("type"),
                "provider_name": request.form.getlist("provider_name"),
                "source": request.form.getlist("source"),
                "cost_of_service": request.form.getlist("cost_of_service"),
            }

            formatted_dates = [
                datetime.strptime(d, "%Y-%m-%d").strftime("%d-%m-%Y")
                for d in service_dates
            ]

            claim = Claim.query.order_by(Claim.id.desc()).first()

            for i in range(len(service_data["service_name"])):
                new_service = Service(
                    claim_id=claim.id,
                    service_date=datetime.strptime(formatted_dates[i], "%d-%m-%Y"),
                    **{k: v[i] for k, v in service_data.items()},
                )
                database.session.add(new_service)
                database.session.commit()

            flash("Claim created successfully.", "success")

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

        return redirect(url_for("home.claim"))
    else:
        data = User.query.with_entities(User.name).all()
        return render_template("home/create_claim.html", all_users=data)


@home_blueprint.route("/claim/<int:id>", methods=["GET"])
def view_claim(id):
    """
    List Claim by id
    """
    claim = Claim.query.get_or_404(id)
    user = User.query.get(claim.user_id)
    services = Service.query.filter_by(claim_id=claim.id).all()
    user_age = datetime.today().year - user.date_of_birth.year

    return render_template(
        "home/view_claim.html",
        claim=claim,
        user=user,
        services=services,
        user_age=user_age,
        title="Claim",
    )


@home_blueprint.route("create_claim/patient_data/", methods=["POST"])
def user_gender_age():
    """
    A route to get a user's birthdate
    and calculate his age
    """
    if request.method == "POST":
        user = User.query.filter_by(name=request.form.get("patient").strip()).first()
        age = datetime.today().year - user.date_of_birth.year

        return jsonify({"age": age, "gender": user.gender})
    return jsonify({"message": "Please use POST request"})
