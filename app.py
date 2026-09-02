from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

app.secret_key = "hostel_management_secret"
APP_VERSION = "v1.1"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():
    return render_template("home.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM admins
            WHERE username = %s
            AND password = %s
            """,
            (username, password)
        )

        admin = cursor.fetchone()

        cursor.close()
        connection.close()

        if admin:

            session["admin_id"] = admin["admin_id"]
            session["username"] = admin["username"]

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM rooms")
    rooms = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM fees")
    fees = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leaves")
    leaves = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        students=students,
        rooms=rooms,
        fees=fees,
        leaves=leaves
    )


# =========================================================
# STUDENTS
# =========================================================

@app.route("/students", methods=["GET", "POST"])
def students():

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]

        cursor.execute(
            """
            INSERT INTO students
            (name, email, phone, course)
            VALUES (%s, %s, %s, %s)
            """,
            (
                name,
                email,
                phone,
                course
            )
        )

        connection.commit()

    cursor.execute(
        """
        SELECT *
        FROM students
        ORDER BY student_id DESC
        """
    )

    student_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "students.html",
        students=student_list
    )


# =========================================================
# EDIT STUDENT
# =========================================================

@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]

        cursor.execute(
            """
            UPDATE students
            SET name = %s,
                email = %s,
                phone = %s,
                course = %s
            WHERE student_id = %s
            """,
            (
                name,
                email,
                phone,
                course,
                student_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("students"))

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE student_id = %s
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "edit_student.html",
        student=student
    )


# =========================================================
# DELETE STUDENT
# =========================================================

@app.route("/students/delete/<int:student_id>")
def delete_student(student_id):

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM students
        WHERE student_id = %s
        """,
        (student_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("students"))


# =========================================================
# ROOMS
# =========================================================

@app.route("/rooms", methods=["GET", "POST"])
def rooms():

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    message = None
    error = None

    if request.method == "POST":

        room_number = request.form["room_number"]
        room_type = request.form["room_type"]
        capacity = request.form["capacity"]

        # Check duplicate room number
        cursor.execute(
            """
            SELECT room_id
            FROM rooms
            WHERE room_number = %s
            """,
            (room_number,)
        )

        existing_room = cursor.fetchone()

        if existing_room:

            error = "Room number already exists."

        else:

            cursor.execute(
                """
                INSERT INTO rooms
                (room_number, room_type, capacity)
                VALUES (%s, %s, %s)
                """,
                (
                    room_number,
                    room_type,
                    capacity
                )
            )

            connection.commit()

            message = "Room added successfully."

    cursor.execute(
        """
        SELECT *
        FROM rooms
        ORDER BY room_id DESC
        """
    )

    room_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "rooms.html",
        rooms=room_list,
        message=message,
        error=error
    )


# =========================================================
# EDIT ROOM
# =========================================================

@app.route("/rooms/edit/<int:room_id>", methods=["GET", "POST"])
def edit_room(room_id):

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        room_number = request.form["room_number"]
        room_type = request.form["room_type"]
        capacity = request.form["capacity"]
        occupied = request.form["occupied"]
        status = request.form["status"]

        cursor.execute(
            """
            UPDATE rooms
            SET room_number = %s,
                room_type = %s,
                capacity = %s,
                occupied = %s,
                status = %s
            WHERE room_id = %s
            """,
            (
                room_number,
                room_type,
                capacity,
                occupied,
                status,
                room_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("rooms"))

    cursor.execute(
        """
        SELECT *
        FROM rooms
        WHERE room_id = %s
        """,
        (room_id,)
    )

    room = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "edit_room.html",
        room=room
    )


# =========================================================
# DELETE ROOM
# =========================================================

@app.route("/rooms/delete/<int:room_id>")
def delete_room(room_id):

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM rooms
        WHERE room_id = %s
        """,
        (room_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("rooms"))


# =========================================================
# ROOM ALLOCATION
# =========================================================

@app.route("/allocations", methods=["GET", "POST"])
def allocations():

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    message = None
    error = None

    if request.method == "POST":

        student_id = request.form["student_id"]
        room_id = request.form["room_id"]
        allocation_date = request.form["allocation_date"]

        # Check whether student already has an active room
        cursor.execute(
            """
            SELECT *
            FROM room_allocations
            WHERE student_id = %s
            AND status = 'Active'
            """,
            (student_id,)
        )

        existing = cursor.fetchone()

        if existing:

            error = "This student already has an active room."

        else:

            # Check room capacity
            cursor.execute(
                """
                SELECT *
                FROM rooms
                WHERE room_id = %s
                """,
                (room_id,)
            )

            room = cursor.fetchone()

            if room is None:

                error = "Room not found."

            elif room["occupied"] >= room["capacity"]:

                error = "This room is already full."

            else:

                # Create allocation
                cursor.execute(
                    """
                    INSERT INTO room_allocations
                    (
                        student_id,
                        room_id,
                        allocation_date,
                        status
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        'Active'
                    )
                    """,
                    (
                        student_id,
                        room_id,
                        allocation_date
                    )
                )

                # Increase occupied count
                new_occupied = room["occupied"] + 1

                if new_occupied >= room["capacity"]:
                    new_status = "Full"
                else:
                    new_status = "Available"

                cursor.execute(
                    """
                    UPDATE rooms
                    SET occupied = %s,
                        status = %s
                    WHERE room_id = %s
                    """,
                    (
                        new_occupied,
                        new_status,
                        room_id
                    )
                )

                connection.commit()

                message = "Room allocated successfully."

    # =====================================================
    # GET STUDENTS
    # =====================================================

    cursor.execute(
        """
        SELECT student_id, name
        FROM students
        ORDER BY name
        """
    )

    student_list = cursor.fetchall()

    # =====================================================
    # GET AVAILABLE ROOMS
    # =====================================================

    cursor.execute(
        """
        SELECT
            room_id,
            room_number,
            room_type,
            capacity,
            occupied
        FROM rooms
        WHERE occupied < capacity
        ORDER BY room_number
        """
    )

    room_list = cursor.fetchall()

    # =====================================================
    # GET ALLOCATIONS
    # =====================================================

    cursor.execute(
        """
        SELECT
            ra.allocation_id,
            s.name AS student_name,
            r.room_number,
            r.room_type,
            ra.allocation_date,
            ra.vacate_date,
            ra.status
        FROM room_allocations ra
        JOIN students s
            ON ra.student_id = s.student_id
        JOIN rooms r
            ON ra.room_id = r.room_id
        ORDER BY ra.allocation_id DESC
        """
    )

    allocation_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "allocations.html",
        students=student_list,
        rooms=room_list,
        allocations=allocation_list,
        message=message,
        error=error
    )


# =========================================================
# FEES
# =========================================================

@app.route("/fees", methods=["GET", "POST"])
def fees():

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    message = None
    error = None

    # ---------------- ADD FEE ----------------

    if request.method == "POST":

        student_id = request.form["student_id"]
        fee_type = request.form["fee_type"]
        amount = request.form["amount"]
        payment_date = request.form["payment_date"]
        last_date = request.form["last_date"]
        payment_status = request.form["payment_status"]

        cursor.execute(
            """
            INSERT INTO fees
            (
                student_id,
                fee_type,
                amount,
                payment_date,
                last_date,
                payment_status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                student_id,
                fee_type,
                amount,
                payment_date,
                last_date,
                payment_status
            )
        )

        connection.commit()

        message = "Fee added successfully."

    # ---------------- GET STUDENTS ----------------

    cursor.execute(
        """
        SELECT student_id, name
        FROM students
        ORDER BY name
        """
    )

    student_list = cursor.fetchall()

    # ---------------- GET FEES ----------------

    cursor.execute(
        """
        SELECT
            f.fee_id,
            s.name AS student_name,
            f.fee_type,
            f.amount,
            f.payment_date,
            f.last_date,
            f.payment_status
        FROM fees f
        JOIN students s
            ON f.student_id = s.student_id
        ORDER BY f.fee_id DESC
        """
    )

    fee_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "fees.html",
        students=student_list,
        fees=fee_list,
        message=message,
        error=error
    )


# =========================================================
# LEAVES
# =========================================================

@app.route("/leaves", methods=["GET", "POST"])
def leaves():

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    message = None
    error = None

    # ---------------- ADD LEAVE ----------------

    if request.method == "POST":

        student_id = request.form["student_id"]
        from_date = request.form["from_date"]
        to_date = request.form["to_date"]
        reason = request.form["reason"]

        cursor.execute(
            """
            INSERT INTO leaves
            (
                student_id,
                from_date,
                to_date,
                reason,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                'Pending'
            )
            """,
            (
                student_id,
                from_date,
                to_date,
                reason
            )
        )

        connection.commit()

        message = "Leave application added successfully."

    # ---------------- GET STUDENTS ----------------

    cursor.execute(
        """
        SELECT
            student_id,
            name
        FROM students
        ORDER BY name
        """
    )

    student_list = cursor.fetchall()

    # ---------------- GET LEAVES ----------------

    cursor.execute(
        """
        SELECT
            l.leave_id,
            s.name AS student_name,
            l.from_date,
            l.to_date,
            l.reason,
            l.status
        FROM leaves l
        JOIN students s
            ON l.student_id = s.student_id
        ORDER BY l.leave_id DESC
        """
    )

    leave_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "leaves.html",
        students=student_list,
        leaves=leave_list,
        message=message,
        error=error
    )


# =========================================================
# DELETE LEAVE
# =========================================================

@app.route("/leaves/delete/<int:leave_id>")
def delete_leave(leave_id):

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM leaves
        WHERE leave_id = %s
        """,
        (leave_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("leaves"))


# =========================================================
# APPROVE LEAVE
# =========================================================

@app.route("/leaves/approve/<int:leave_id>")
def approve_leave(leave_id):

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE leaves
        SET status = 'Approved'
        WHERE leave_id = %s
        """,
        (leave_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("leaves"))


# =========================================================
# REJECT LEAVE
# =========================================================

@app.route("/leaves/reject/<int:leave_id>")
def reject_leave(leave_id):

    if "admin_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE leaves
        SET status = 'Rejected'
        WHERE leave_id = %s
        """,
        (leave_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("leaves"))


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)