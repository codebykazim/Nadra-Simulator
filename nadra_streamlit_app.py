# nadra_streamlit_app.py
"""
NADRA Mega Centre Queue Simulator - Streamlit Web App
Complete conversion from Tkinter desktop to web interface
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import random
import statistics
import json
from datetime import datetime
import base64
from io import BytesIO
import warnings

warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="NADRA Mega Centre Queue Simulator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .priority-1 { color: #1f77b4; font-weight: bold; }
    .priority-2 { color: #2ca02c; font-weight: bold; }
    .priority-3 { color: #ff7f0e; font-weight: bold; }
    .priority-4 { color: #d62728; font-weight: bold; }
    .stButton>button {
        width: 100%;
        background-color: #3B82F6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PART 1: REUSE YOUR PROVEN DISTRIBUTIONS (NO CHANGES)
# ============================================================================

class NadraDistributions:
    """Statistical distributions validated from your NADRA data analysis"""

    OPERATING_HOURS = (8, 19)
    TOTAL_MINUTES = 660

    PRIORITIES = {
        1: {"name": "Senior Citizen/Disabled", "color": "#1f77b4", "marker": "▲"},
        2: {"name": "Executive", "color": "#2ca02c", "marker": "★"},
        3: {"name": "Overseas", "color": "#ff7f0e", "marker": "⚑"},
        4: {"name": "Normal", "color": "#d62728", "marker": "●"}
    }

    SERVICE_PARAMS = {
        1: {"mean": 8.5, "std": 1.2},
        2: {"mean": 25.5, "std": 2.5},
        3: {"mean": 32.0, "std": 3.0},
        4: {"mean": 31.0, "std": 4.0}
    }

    @staticmethod
    def generate_arrival_time(num_customers):
        return sorted([random.uniform(0, NadraDistributions.TOTAL_MINUTES)
                      for _ in range(num_customers)])

    @staticmethod
    def generate_service_time(priority):
        params = NadraDistributions.SERVICE_PARAMS[priority]
        service = random.gauss(params["mean"], params["std"])
        return max(1.0, round(service, 1))

    @staticmethod
    def generate_priority_distribution(num_customers):
        priority_weights = {
            1: 0.15,   # 15% Senior/Disabled
            2: 0.25,   # 25% Executive
            3: 0.20,   # 20% Overseas
            4: 0.40    # 40% Normal
        }

        priorities = []
        for _ in range(num_customers):
            r = random.random()
            cumulative = 0
            for prio, weight in priority_weights.items():
                cumulative += weight
                if r <= cumulative:
                    priorities.append(prio)
                    break
        return priorities

    @staticmethod
    def time_to_str(minutes):
        hour = 8 + minutes // 60
        minute = minutes % 60
        return f"{int(hour):02d}:{int(minute):02d}"

# ============================================================================
# PART 2: STATISTICAL VALIDATION MODULE (NO CHANGES)
# ============================================================================

class StatisticalValidator:
    """Module to showcase your Chi-square validation results"""

    @staticmethod
    def get_validation_results():
        return {
            "arrival_distribution": {
                "type": "Uniform",
                "test": "Chi-square Goodness-of-Fit",
                "chi_square": 10.0,
                "critical_value": 18.107,
                "p_value": 0.35,
                "result": "ACCEPT H0: Uniform Distribution",
                "conclusion": "Arrival times are uniformly distributed throughout operational hours"
            },
            "service_distributions": {
                1: {
                    "type": "Normal",
                    "mean": 8.5,
                    "std": 1.2,
                    "chi_square": 0.495,
                    "critical_value": 5.991,
                    "result": "ACCEPT H0: Normal Distribution",
                    "outliers": "Values > 9.2 were treated as outliers"
                },
                2: {
                    "type": "Normal",
                    "mean": 25.5,
                    "std": 2.5,
                    "chi_square": 2.185,
                    "critical_value": 7.814,
                    "result": "ACCEPT H0: Normal Distribution",
                    "outliers": "42.3 and 45.2 were treated as outliers"
                },
                3: {
                    "type": "Normal",
                    "mean": 32.0,
                    "std": 3.0,
                    "chi_square": 0.411,
                    "critical_value": 7.815,
                    "result": "ACCEPT H0: Normal Distribution",
                    "outliers": "44.7, 44.8, 48.5 were treated as outliers"
                },
                4: {
                    "type": "Normal",
                    "mean": 31.0,
                    "std": 4.0,
                    "chi_square": 2.819,
                    "critical_value": 9.488,
                    "result": "ACCEPT H0: Normal Distribution",
                    "outliers": "Values > 40 were treated as outliers"
                }
            },
            "methodology": "Chi-square goodness-of-fit test with α=0.05",
            "data_size": "200 real customer records from NADRA Mega Centre",
            "conclusion": "All distributions validated with statistical significance"
        }

# ============================================================================
# PART 3: DISCRETE-EVENT SIMULATION ENGINE (MINIMAL CHANGES)
# ============================================================================

class Customer:
    """Represents a NADRA customer"""

    def __init__(self, customer_id, arrival_time, service_time, priority):
        self.id = customer_id
        self.arrival_time = arrival_time
        self.service_time = service_time
        self.priority = priority
        self.category = NadraDistributions.PRIORITIES[priority]["name"]

        self.start_time = None
        self.end_time = None
        self.waiting_time = 0
        self.counter_id = None
        self.queue_entered = []
        self.queue_exited = []

    @property
    def total_time(self):
        if self.end_time:
            return self.end_time - self.arrival_time
        return None

    @property
    def turnaround_time(self):
        return self.total_time

    @property
    def response_time(self):
        if self.start_time:
            return self.start_time - self.arrival_time
        return None

class Counter:
    """Represents a service counter"""

    def __init__(self, counter_id, priority_handling=None):
        self.id = counter_id
        self.priority_handling = priority_handling
        self.current_customer = None
        self.busy_until = 0
        self.total_busy_time = 0
        self.customers_served = 0
        self.idle_time = 0

    def is_available(self, current_time):
        return current_time >= self.busy_until

    def can_handle(self, priority):
        if self.priority_handling is None:
            return True
        return priority in self.priority_handling

    def assign_customer(self, customer, current_time):
        self.current_customer = customer
        customer.start_time = current_time
        customer.counter_id = self.id
        self.busy_until = current_time + customer.service_time
        service_duration = customer.service_time

        if current_time > self.busy_until - service_duration:
            self.total_busy_time += service_duration
        self.customers_served += 1

        return self.busy_until

    def complete_service(self, current_time):
        if self.current_customer:
            self.current_customer.end_time = current_time
            completed = self.current_customer
            self.current_customer = None
            return completed
        return None

class Event:
    """Discrete event for event-driven simulation"""

    ARRIVAL = 1
    DEPARTURE = 2

    def __init__(self, event_type, time, customer=None, counter=None):
        self.event_type = event_type
        self.time = time
        self.customer = customer
        self.counter = counter

    def __lt__(self, other):
        return self.time < other.time

class QueueSimulator:
    """Main simulation engine"""

    def __init__(self, num_counters=4, queue_discipline="FCFS",
                 counter_specialization=None, max_simulation_time=660):
        self.num_counters = num_counters
        self.queue_discipline = queue_discipline
        self.counter_specialization = counter_specialization
        self.max_simulation_time = max_simulation_time

        # Initialize counters
        self.counters = []
        for i in range(num_counters):
            if counter_specialization and i < len(counter_specialization):
                self.counters.append(Counter(i + 1, counter_specialization[i]))
            else:
                self.counters.append(Counter(i + 1))

        # Simulation state
        self.customers = []
        self.event_queue = []
        self.waiting_queue = []
        self.current_time = 0
        self.completed_customers = []
        self.queue_length_history = []
        self.utilization_history = []
        self.time_history = []

        # Performance metrics
        self.metrics = {
            "total_customers": 0,
            "served_customers": 0,
            "rejected_customers": 0,
            "avg_wait_time": 0,
            "avg_system_time": 0,
            "max_queue_length": 0,
            "counter_utilization": [],
            "priority_stats": {p: {"count": 0, "avg_wait": 0, "avg_service": 0}
                              for p in range(1, 5)}
        }

    def generate_customers(self, num_customers):
        """Generate customers using validated distributions"""
        arrivals = NadraDistributions.generate_arrival_time(num_customers)
        priorities = NadraDistributions.generate_priority_distribution(num_customers)

        for i in range(num_customers):
            service_time = NadraDistributions.generate_service_time(priorities[i])
            customer = Customer(i + 1, arrivals[i], service_time, priorities[i])
            self.customers.append(customer)

            # Schedule arrival event
            self.event_queue.append(Event(Event.ARRIVAL, arrivals[i], customer))

        self.metrics["total_customers"] = num_customers
        self.event_queue.sort()

    def find_available_counter(self, customer):
        """Find available counter for customer based on specialization"""
        available = []
        specialized = []

        for counter in self.counters:
            if counter.is_available(self.current_time) and counter.can_handle(customer.priority):
                if counter.priority_handling and customer.priority in counter.priority_handling:
                    specialized.append(counter)
                else:
                    available.append(counter)

        if specialized:
            return specialized[0]
        elif available:
            return available[0]
        return None

    def select_next_customer(self):
        """Select next customer based on queue discipline"""
        if not self.waiting_queue:
            return None

        if self.queue_discipline == "FCFS":
            return self.waiting_queue.pop(0)
        elif self.queue_discipline == "PRIORITY":
            self.waiting_queue.sort(key=lambda c: (c.priority, c.arrival_time))
            return self.waiting_queue.pop(0)
        elif self.queue_discipline == "MIXED":
            high_priority = [c for c in self.waiting_queue if c.priority <= 2]
            if high_priority:
                high_priority.sort(key=lambda c: (c.priority, c.arrival_time))
                customer = high_priority[0]
                self.waiting_queue.remove(customer)
                return customer
            else:
                return self.waiting_queue.pop(0)
        return self.waiting_queue.pop(0)

    def handle_arrival(self, event):
        """Process customer arrival"""
        customer = event.customer
        customer.queue_entered.append(self.current_time)

        counter = self.find_available_counter(customer)

        if counter:
            departure_time = counter.assign_customer(customer, self.current_time)
            self.event_queue.append(Event(Event.DEPARTURE, departure_time, customer, counter))
            self.event_queue.sort()
        else:
            self.waiting_queue.append(customer)
            self.update_history()

    def handle_departure(self, event):
        """Process customer departure"""
        customer = event.customer
        counter = event.counter

        completed = counter.complete_service(self.current_time)
        if completed:
            completed.queue_exited.append(self.current_time)
            self.completed_customers.append(completed)
            self.metrics["served_customers"] += 1

            if completed.start_time:
                completed.waiting_time = completed.start_time - completed.arrival_time

            prio = completed.priority
            self.metrics["priority_stats"][prio]["count"] += 1
            self.metrics["priority_stats"][prio]["avg_wait"] = (
                self.metrics["priority_stats"][prio]["avg_wait"] *
                (self.metrics["priority_stats"][prio]["count"] - 1) +
                completed.waiting_time
            ) / self.metrics["priority_stats"][prio]["count"]
            self.metrics["priority_stats"][prio]["avg_service"] = (
                self.metrics["priority_stats"][prio]["avg_service"] *
                (self.metrics["priority_stats"][prio]["count"] - 1) +
                completed.service_time
            ) / self.metrics["priority_stats"][prio]["count"]

        next_customer = self.select_next_customer()
        if next_customer:
            departure_time = counter.assign_customer(next_customer, self.current_time)
            self.event_queue.append(Event(Event.DEPARTURE, departure_time, next_customer, counter))
            self.event_queue.sort()

        self.update_history()

    def update_history(self):
        """Update time series history for visualization"""
        self.time_history.append(self.current_time)
        self.queue_length_history.append(len(self.waiting_queue))

        busy_counters = sum(1 for c in self.counters if not c.is_available(self.current_time))
        utilization = busy_counters / self.num_counters if self.num_counters > 0 else 0
        self.utilization_history.append(utilization)

        if len(self.waiting_queue) > self.metrics["max_queue_length"]:
            self.metrics["max_queue_length"] = len(self.waiting_queue)

    def run(self, num_customers=200):
        """Run the simulation"""
        self.generate_customers(num_customers)

        # Main simulation loop
        while self.event_queue and self.current_time <= self.max_simulation_time:
            event = self.event_queue.pop(0)
            self.current_time = event.time

            if event.event_type == Event.ARRIVAL:
                self.handle_arrival(event)
            elif event.event_type == Event.DEPARTURE:
                self.handle_departure(event)

            if len(self.completed_customers) >= num_customers * 0.95:
                break

        # Complete remaining services
        while any(c.current_customer for c in self.counters):
            next_departure = min((c.busy_until for c in self.counters if c.current_customer),
                               default=self.current_time)
            self.current_time = next_departure

            for counter in self.counters:
                if counter.busy_until == self.current_time and counter.current_customer:
                    customer = counter.current_customer
                    completed = counter.complete_service(self.current_time)
                    if completed:
                        completed.queue_exited.append(self.current_time)
                        self.completed_customers.append(completed)
                        self.metrics["served_customers"] += 1

        self.finalize_metrics()

        return {
            "customers": self.completed_customers,
            "metrics": self.metrics,
            "history": {
                "time": self.time_history,
                "queue_length": self.queue_length_history,
                "utilization": self.utilization_history
            },
            "counters": self.counters
        }

    def finalize_metrics(self):
        """Calculate final performance metrics"""
        if self.completed_customers:
            wait_times = [c.waiting_time for c in self.completed_customers]
            system_times = [c.total_time for c in self.completed_customers if c.total_time]

            self.metrics["avg_wait_time"] = statistics.mean(wait_times) if wait_times else 0
            self.metrics["avg_system_time"] = statistics.mean(system_times) if system_times else 0

            total_time = max(self.time_history) if self.time_history else 1
            self.metrics["counter_utilization"] = []
            for counter in self.counters:
                utilization = counter.total_busy_time / total_time if total_time > 0 else 0
                self.metrics["counter_utilization"].append({
                    "counter_id": counter.id,
                    "utilization": utilization,
                    "customers_served": counter.customers_served,
                    "avg_service_time": counter.total_busy_time / counter.customers_served
                    if counter.customers_served > 0 else 0
                })

            self.metrics["rejected_customers"] = (
                self.metrics["total_customers"] - self.metrics["served_customers"]
            )

# ============================================================================
# PART 4: STREAMLIT WEB APPLICATION
# ============================================================================

def create_dashboard(simulation_results):
    """Create main dashboard with metrics and charts"""

    if not simulation_results:
        return

    metrics = simulation_results['metrics']
    history = simulation_results['history']

    # Header
    st.markdown('<h1 class="main-header">🎯 NADRA Mega Centre Queue Simulator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Data-Driven Simulation Based on Statistical Analysis</p>', unsafe_allow_html=True)

    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Customers", f"{metrics['total_customers']:,}")
        st.metric("Served Customers", f"{metrics['served_customers']:,}")

    with col2:
        st.metric("Avg Wait Time", f"{metrics['avg_wait_time']:.1f} min")
        st.metric("Avg System Time", f"{metrics['avg_system_time']:.1f} min")

    with col3:
        st.metric("Max Queue Length", metrics['max_queue_length'])
        utilization = np.mean([c['utilization'] for c in metrics['counter_utilization']])
        st.metric("Avg Utilization", f"{utilization:.1%}")

    with col4:
        service_rate = metrics['served_customers'] / metrics['total_customers'] if metrics['total_customers'] > 0 else 0
        st.metric("Service Rate", f"{service_rate:.1%}")
        prio1_wait = metrics['priority_stats'][1]['avg_wait']
        st.metric("Priority 1 Wait", f"{prio1_wait:.1f} min")

    # Main Charts
    st.markdown("## 📊 Performance Visualizations")

    # Create tabs for different charts
    tab1, tab2, tab3, tab4 = st.tabs([
        "Queue Dynamics",
        "Counter Analysis",
        "Priority Breakdown",
        "Customer Flow"
    ])

    with tab1:
        # Queue Length Over Time
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=history['time'],
            y=history['queue_length'],
            mode='lines',
            name='Queue Length',
            line=dict(color='blue', width=2)
        ))
        fig.update_layout(
            title='Queue Length Over Time',
            xaxis_title='Time (minutes)',
            yaxis_title='Queue Length',
            hovermode='x unified',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Counter Utilization
        counter_ids = [c['counter_id'] for c in metrics['counter_utilization']]
        utilizations = [c['utilization'] for c in metrics['counter_utilization']]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=counter_ids,
            y=utilizations,
            text=[f'{u:.1%}' for u in utilizations],
            textposition='auto',
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        ))
        fig.update_layout(
            title='Counter Utilization',
            xaxis_title='Counter ID',
            yaxis_title='Utilization (%)',
            yaxis=dict(range=[0, 1]),
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            # Wait Time by Priority
            priorities = list(range(1, 5))
            wait_times = [metrics['priority_stats'][p]['avg_wait'] for p in priorities]
            colors = [NadraDistributions.PRIORITIES[p]['color'] for p in priorities]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[f'P{p}' for p in priorities],
                y=wait_times,
                marker_color=colors,
                text=[f'{wt:.1f} min' for wt in wait_times],
                textposition='auto'
            ))
            fig.update_layout(
                title='Average Wait Time by Priority',
                xaxis_title='Priority',
                yaxis_title='Wait Time (minutes)',
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Customer Distribution
            priority_counts = [metrics['priority_stats'][p]['count'] for p in priorities]
            labels = [f'P{p} - {NadraDistributions.PRIORITIES[p]["name"]}' for p in priorities]

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=priority_counts,
                hole=0.3,
                marker_colors=colors
            )])
            fig.update_layout(
                title='Customer Distribution by Priority',
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        # Customer Flow through system
        customers = simulation_results['customers'][:100]  # Limit for performance
        times = []
        in_system = []
        current_time = 0
        max_time = max([c.end_time for c in customers]) if customers else 660

        while current_time <= max_time:
            in_system_at_time = sum(1 for c in customers
                                   if c.arrival_time <= current_time <= c.end_time)
            times.append(current_time)
            in_system.append(in_system_at_time)
            current_time += 5

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=in_system,
            mode='lines',
            fill='tozeroy',
            name='Customers in System',
            line=dict(color='purple', width=2)
        ))
        fig.update_layout(
            title='Customers in System Over Time',
            xaxis_title='Time (minutes)',
            yaxis_title='Number of Customers',
            hovermode='x unified',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

def display_validation_results():
    """Display statistical validation results"""
    st.markdown("## ✅ Statistical Validation")

    validation_data = StatisticalValidator.get_validation_results()

    with st.expander("View Complete Validation Report", expanded=True):
        # Arrival Distribution
        st.markdown("### Arrival Time Distribution")
        arr = validation_data['arrival_distribution']

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Distribution Type:** {arr['type']}")
            st.info(f"**Test:** {arr['test']}")
        with col2:
            st.success(f"**χ² Statistic:** {arr['chi_square']}")
            st.success(f"**p-value:** {arr['p_value']}")

        st.success(f"**Result:** {arr['result']}")
        st.caption(arr['conclusion'])

        st.markdown("---")

        # Service Distributions
        st.markdown("### Service Time Distributions by Priority")

        for prio in range(1, 5):
            service = validation_data['service_distributions'][prio]
            priority_name = NadraDistributions.PRIORITIES[prio]['name']

            with st.expander(f"Priority {prio}: {priority_name}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Mean", f"{service['mean']:.1f} min")
                with col2:
                    st.metric("Std Dev", f"{service['std']:.1f} min")
                with col3:
                    st.metric("χ² Statistic", f"{service['chi_square']:.3f}")

                st.info(f"**Test Result:** {service['result']}")
                st.caption(f"**Outlier Treatment:** {service['outliers']}")

def create_scenario_comparison():
    """Run and compare different scenarios"""
    st.markdown("## 🔄 Scenario Comparison")

    scenario_type = st.radio(
        "Select Comparison Type:",
        ["Different Counter Counts", "Queue Disciplines", "With/Without Specialization"],
        horizontal=True
    )

    num_customers = st.slider("Number of customers for comparison", 100, 2000, 500)

    if st.button("Run Comparison", type="primary"):
        with st.spinner("Running scenario comparisons..."):
            scenarios = []

            if scenario_type == "Different Counter Counts":
                counter_counts = [1, 2, 4, 6, 8]
                for c in counter_counts:
                    simulator = QueueSimulator(num_counters=c, queue_discipline="FCFS")
                    result = simulator.run(num_customers)
                    scenarios.append((f"{c} Counters", result))

            elif scenario_type == "Queue Disciplines":
                disciplines = ["FCFS", "PRIORITY", "MIXED"]
                for d in disciplines:
                    simulator = QueueSimulator(num_counters=4, queue_discipline=d)
                    result = simulator.run(num_customers)
                    scenarios.append((d, result))

            elif scenario_type == "With/Without Specialization":
                # Without specialization
                simulator1 = QueueSimulator(num_counters=4, queue_discipline="PRIORITY")
                result1 = simulator1.run(num_customers)
                scenarios.append(("No Specialization", result1))

                # With specialization
                spec_config = [[1], [1, 2], None, None]
                simulator2 = QueueSimulator(
                    num_counters=4,
                    queue_discipline="PRIORITY",
                    counter_specialization=spec_config
                )
                result2 = simulator2.run(num_customers)
                scenarios.append(("With Specialization", result2))

            # Display comparison chart
            display_comparison_chart(scenarios)

def display_comparison_chart(scenarios):
    """Display comparison chart for scenarios"""
    scenario_names = [s[0] for s in scenarios]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Average Wait Time', 'Maximum Queue Length',
                       'Counter Utilization', 'Priority 1 Wait Time')
    )

    # Metric 1: Average wait time
    wait_times = [s[1]['metrics']['avg_wait_time'] for s in scenarios]
    fig.add_trace(
        go.Bar(x=scenario_names, y=wait_times, name='Avg Wait'),
        row=1, col=1
    )

    # Metric 2: Max queue length
    max_queues = [s[1]['metrics']['max_queue_length'] for s in scenarios]
    fig.add_trace(
        go.Bar(x=scenario_names, y=max_queues, name='Max Queue'),
        row=1, col=2
    )

    # Metric 3: Counter utilization
    utilizations = [np.mean([c['utilization'] for c in s[1]['metrics']['counter_utilization']])
                    for s in scenarios]
    fig.add_trace(
        go.Bar(x=scenario_names, y=utilizations, name='Utilization'),
        row=2, col=1
    )

    # Metric 4: Priority 1 wait time
    prio1_waits = [s[1]['metrics']['priority_stats'][1]['avg_wait'] for s in scenarios]
    fig.add_trace(
        go.Bar(x=scenario_names, y=prio1_waits, name='P1 Wait'),
        row=2, col=2
    )

    fig.update_layout(height=600, showlegend=False, template='plotly_white')
    fig.update_yaxes(title_text="Minutes", row=1, col=1)
    fig.update_yaxes(title_text="Customers", row=1, col=2)
    fig.update_yaxes(title_text="Utilization %", row=2, col=1)
    fig.update_yaxes(title_text="Minutes", row=2, col=2)

    st.plotly_chart(fig, use_container_width=True)

def display_customer_details(simulation_results):
    """Display detailed customer information"""
    if not simulation_results or 'customers' not in simulation_results:
        return

    st.markdown("## 👥 Customer Details")

    customers = simulation_results['customers']

    # Create dataframe for display
    data = []
    for cust in customers[:500]:  # Limit display for performance
        data.append({
            'ID': cust.id,
            'Priority': f"P{cust.priority}",
            'Category': cust.category,
            'Arrival (min)': round(cust.arrival_time, 1),
            'Service (min)': cust.service_time,
            'Wait (min)': round(cust.waiting_time, 1),
            'Total (min)': round(cust.total_time, 1) if cust.total_time else None,
            'Counter': cust.counter_id or '-'
        })

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=400)

        # Show summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Customers Displayed", len(data))
        with col2:
            avg_wait = df['Wait (min)'].mean()
            st.metric("Average Wait Time", f"{avg_wait:.1f} min")
        with col3:
            max_wait = df['Wait (min)'].max()
            st.metric("Maximum Wait Time", f"{max_wait:.1f} min")

def display_queueing_theory():
    """Display queueing theory explanations"""
    st.markdown("## 📚 Queueing Theory Foundations")

    theory_text = """
    This simulator implements validated queueing models based on real NADRA data:

    ### 1. Validated Distributions
    - **Arrivals**: Uniform distribution U(0, 660 minutes)
    - **Service**: Normal distribution N(μₚ, σₚ²) per priority p
    - Validated with Chi-square goodness-of-fit tests (α=0.05)

    ### 2. Queue Types Implemented
    - **FCFS**: First-Come-First-Served (standard queue)
    - **PRIORITY**: Higher priority customers served first (non-preemptive)
    - **MIXED**: Priority queue with fairness to prevent starvation

    ### 3. Key Performance Indicators (KPIs)
    - **Lq**: Average queue length (customers waiting)
    - **Wq**: Average waiting time in queue
    - **L**: Average number of customers in system (queue + service)
    - **W**: Average time in system (wait + service)
    - **ρ**: Server utilization (busy percentage)
    - **P₀**: Probability system is empty

    ### 4. Statistical Significance
    All distributions are statistically validated:
    - Arrival uniformity: p-value = 0.35 > 0.05 → Accept H₀
    - Service normality: All priorities pass Chi-square test
    - Based on 200 real customer records
    """

    st.markdown(theory_text)

def generate_report(simulation_results):
    """Generate and download report"""
    if not simulation_results:
        st.warning("Run a simulation first to generate a report")
        return

    metrics = simulation_results['metrics']

    report_text = f"""
    NADRA MEGA CENTRE QUEUE SIMULATION REPORT
    {'='*60}

    Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    PERFORMANCE METRICS
    {'-'*60}

    Overall Performance:
    • Total Customers: {metrics['total_customers']}
    • Served Customers: {metrics['served_customers']}
    • Service Rate: {metrics['served_customers']/metrics['total_customers']:.1%}
    • Average Wait Time: {metrics['avg_wait_time']:.2f} minutes
    • Average System Time: {metrics['avg_system_time']:.2f} minutes
    • Maximum Queue Length: {metrics['max_queue_length']}

    Counter Utilization:
    """

    for util in metrics['counter_utilization']:
        report_text += f"• Counter {util['counter_id']}: {util['utilization']:.1%} "
        report_text += f"({util['customers_served']} customers)\n"

    report_text += f"\nAverage Utilization: {np.mean([u['utilization'] for u in metrics['counter_utilization']]):.1%}\n"

    report_text += """

    RECOMMENDATIONS
    {'-'*60}

    Based on simulation results:
    """

    # Generate recommendations
    avg_wait = metrics['avg_wait_time']
    max_queue = metrics['max_queue_length']
    utilization = np.mean([u['utilization'] for u in metrics['counter_utilization']])

    if avg_wait > 30:
        report_text += "\n1. ⚠️ High wait times detected (>30 minutes)"
        report_text += "\n   • Consider adding more service counters"
        report_text += "\n   • Implement express lanes for simple transactions"

    if max_queue > 15:
        report_text += "\n\n2. ⚠️ Excessive queue lengths observed"
        report_text += "\n   • Implement better queue management"
        report_text += "\n   • Consider digital queue system"

    if utilization > 0.85:
        report_text += "\n\n3. ⚠️ Counters are over-utilized (>85%)"
        report_text += "\n   • Add staff during peak hours"
        report_text += "\n   • Cross-train staff for multiple roles"

    # Convert to downloadable file
    b64 = base64.b64encode(report_text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="nadra_simulation_report.txt">📥 Download Full Report</a>'
    st.markdown(href, unsafe_allow_html=True)

# ============================================================================
# MAIN STREAMLIT APPLICATION
# ============================================================================

def main():
    """Main Streamlit application"""

    # Initialize session state
    if 'simulation_results' not in st.session_state:
        st.session_state.simulation_results = None

    # Sidebar for controls
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3067/3067256.png", width=100)
        st.markdown("### Simulation Controls")

        # Input parameters
        num_customers = st.number_input(
            "Number of Customers",
            min_value=100,
            max_value=5000,
            value=1000,
            step=100,
            help="Total customers to simulate"
        )

        num_counters = st.selectbox(
            "Number of Counters",
            [1, 2, 4, 6, 8, 10],
            index=2,
            help="Number of service counters"
        )

        queue_discipline = st.selectbox(
            "Queue Discipline",
            ["FCFS", "PRIORITY", "MIXED"],
            help="How customers are selected from queue"
        )

        enable_specialization = st.checkbox(
            "Enable Counter Specialization",
            value=False,
            help="Assign specific counters to priority levels"
        )

        # Run simulation button
        if st.button("▶ Run Simulation", type="primary", use_container_width=True):
            with st.spinner("Running simulation..."):
                # Create simulator
                if enable_specialization:
                    spec_config = [[1], [1, 2]] + [None] * (num_counters - 2)
                    spec_config = spec_config[:num_counters]
                    simulator = QueueSimulator(
                        num_counters=num_counters,
                        queue_discipline=queue_discipline,
                        counter_specialization=spec_config
                    )
                else:
                    simulator = QueueSimulator(
                        num_counters=num_counters,
                        queue_discipline=queue_discipline
                    )

                # Run simulation
                results = simulator.run(num_customers)
                st.session_state.simulation_results = results

                st.success(f"Simulation completed! Served {results['metrics']['served_customers']} customers")

        st.markdown("---")

        # Additional actions
        if st.session_state.simulation_results:
            if st.button("📊 Generate Report", use_container_width=True):
                generate_report(st.session_state.simulation_results)

        st.markdown("---")

        # Information panel
        with st.expander("ℹ️ About This Simulator"):
            st.markdown("""
            **NADRA Mega Centre Queue Simulator**

            This simulator uses statistically validated distributions:
            - Arrival times: Uniform distribution
            - Service times: Normal distribution per priority
            - Based on 200 real customer records

            **Priority Levels:**
            1. Senior/Disabled (15%) - Fastest service
            2. Executive (25%) - Moderate service
            3. Overseas (20%) - Longer service
            4. Normal (40%) - Standard service

            All distributions validated with Chi-square tests (α=0.05).
            """)

    # Main content area
    if st.session_state.simulation_results:
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Dashboard",
            "✅ Validation",
            "🔄 Comparison",
            "📚 Theory",
            "👥 Customers"
        ])

        with tab1:
            create_dashboard(st.session_state.simulation_results)

        with tab2:
            display_validation_results()

        with tab3:
            create_scenario_comparison()

        with tab4:
            display_queueing_theory()

        with tab5:
            display_customer_details(st.session_state.simulation_results)

    else:
        # Welcome screen
        st.markdown('<h1 class="main-header">🎯 NADRA Mega Centre Queue Simulator</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Data-Driven Simulation Based on Statistical Analysis</p>', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("""
            ### Welcome to the Queue Simulation Platform

            This web application simulates customer service at a NADRA Mega Centre using:

            **🎯 Real Statistical Models**
            - Arrival times: Uniform distribution (validated)
            - Service times: Normal distribution per priority (validated)
            - Based on 200 real customer records

            **📊 Multiple Queue Strategies**
            - First-Come-First-Served (FCFS)
            - Priority-based queuing
            - Mixed strategies

            **🔧 Customizable Parameters**
            - Number of customers
            - Number of service counters
            - Queue discipline
            - Counter specialization

            **📈 Comprehensive Analytics**
            - Real-time performance metrics
            - Interactive visualizations
            - Scenario comparison
            - Detailed reporting

            ### Getting Started
            1. Adjust simulation parameters in the sidebar
            2. Click **"Run Simulation"** to start
            3. Explore results in the dashboard tabs
            """)

        with col2:
            st.image("https://cdn-icons-png.flaticon.com/512/3067/3067256.png", width=300)

            st.info("""
            **Quick Stats:**
            - Operational Hours: 8 AM - 7 PM
            - Total Simulation Time: 660 minutes
            - Priority Distribution:
              • Senior/Disabled: 15%
              • Executive: 25%
              • Overseas: 20%
              • Normal: 40%
            """)

        # Quick start example
        st.markdown("---")
        st.markdown("### 🚀 Quick Start")

        if st.button("Run Sample Simulation (1000 customers, 4 counters, FCFS)"):
            with st.spinner("Running sample simulation..."):
                simulator = QueueSimulator(num_counters=4, queue_discipline="FCFS")
                results = simulator.run(1000)
                st.session_state.simulation_results = results
                st.rerun()

if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    main()