<!-- Bootstrap JS Bundle (includes Popper) -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>



<!DOCTYPE html>
{% load static %}
<html lang="en">
<head>

    <style>
        .bounce {
          display: flex;
          justify-content: center;
        }
        .bounce-ball {
          width: 15px;
          height: 15px;
          margin: 0 5px;
          border-radius: 50%;
          background-color: #007bff;
          animation: bounce 0.6s infinite alternate;
        }
        .bounce-ball:nth-child(1) {
          animation-delay: 0s;
        }
        .bounce-ball:nth-child(2) {
          animation-delay: 0.2s;
        }
        .bounce-ball:nth-child(3) {
          animation-delay: 0.4s;
        }
        @keyframes bounce {
          0% {
            transform: translateY(0);
          }
          100% {
            transform: translateY(-20px);
          }
        }
      </style>

<style>
        body {
            font-family: Arial, sans-serif;
        }
        .line {
            fill: none;
            stroke: steelblue;
            stroke-width: 2px;
        }
        .label {
            font-size: 12px;
            font-weight: bold;
        }
        .axis path,
        .axis line {
            fill: none;
            shape-rendering: crispEdges;
        }
        .axis text {
            font-size: 12px;
        }
        .chart-container {
            margin-top: 20px;
        }
    </style>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <title>{% block title %}Predictive Maintenance{% endblock %}</title>
    <link href="{% static 'css/styles.css' %}" rel="stylesheet" />
    <link rel="icon" type="image/png" href="{% static 'images/logo.png' %}" />
    <!-- SweetAlert2 CSS -->
<!-- <link href="https://cdn.jsdelivr.net/npm/sweetalert2@11.4.14/dist/sweetalert2.min.css" rel="stylesheet"> -->
<link href="{% static 'sweetalert2/sweetalert2.min.css' %}" rel="stylesheet">

<!-- SweetAlert2 JS -->
<!-- <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.4.14/dist/sweetalert2.all.min.js"></script> -->
<script src="{% static 'sweetalert2/sweetalert2.all.min.js' %}"></script>
    <!-- <script src="https://cdn.jsdelivr.net/npm/chart.js"></script> -->
  <script src="{% static 'chartjs/chart.min.js' %}"></script>


<!--    <script src="https://d3js.org/d3.v7.min.js"></script>-->
    <!-- <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.13.0/js/all.min.js" crossorigin="anonymous"></script> -->
    
    <link href="{% static 'fontawesome/css/all.min.css' %}" rel="stylesheet">
    {% block extra_head %}{% endblock %}
</head>
<body class="sb-nav-fixed">
    <!-- Include Navigation -->
    {% include 'partials/navbar.html' %}
    <div id="layoutSidenav">
        <!-- Include Sidebar -->
        {% include 'partials/sidebar.html' %}
        <div id="layoutSidenav_content">
            <main>
                {% block content %}{% endblock %}
            </main>
            <!-- Include Footer -->
            {% include 'partials/footer.html' %}
        </div>
    </div>
<!--    <script src="https://code.jquery.com/jquery-3.5.1.min.js" crossorigin="anonymous"></script>-->
    <!-- <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.bundle.min.js" crossorigin="anonymous"></script>
    <script src="{% static 'js/scripts.js' %}"></script> -->

    <script src="{% static 'js/jquery-3.6.0.min.js' %}"></script>

    <!-- Link to local D3.js -->
    <script src="{% static 'js/d3.v7.min.js' %}"></script>

    <!-- Link to local Bootstrap JS -->
    <script src="{% static 'js/bootstrap.bundle.min.js' %}" crossorigin="anonymous"></script>

    <!-- Link to your custom script.js -->
    <script src="{% static 'js/scripts.js' %}"></script>
    {% block javascript %}{% endblock %}
</body>
</html>
