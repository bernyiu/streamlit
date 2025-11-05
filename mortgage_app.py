import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Mortgage Calculator",
    page_icon="🏠",
    layout="wide"
)

# Title and description
st.title("🏠 Interactive Mortgage Payment Calculator")
st.markdown("Calculate your mortgage payments and view detailed amortization schedule")

# Sidebar for inputs
st.sidebar.header("Loan Parameters")

# Input fields
loan_principal = st.sidebar.number_input(
    "Loan Principal Amount ($)",
    min_value=1000,
    max_value=10000000,
    value=300000,
    step=10000,
    help="Enter the total loan amount"
)

annual_rate = st.sidebar.number_input(
    "Annual Interest Rate (%)",
    min_value=0.0,
    max_value=20.0,
    value=6.5,
    step=0.1,
    format="%.2f",
    help="Enter the annual interest rate as a percentage"
)

loan_years = st.sidebar.number_input(
    "Loan Term (Years)",
    min_value=1,
    max_value=50,
    value=30,
    step=1,
    help="Enter the loan term in years"
)

# Add a calculate button
calculate_button = st.sidebar.button("Calculate", type="primary", use_container_width=True)

# Function to calculate monthly payment
def calculate_monthly_payment(principal, annual_rate, years):
    """Calculate the fixed monthly mortgage payment."""
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                         ((1 + monthly_rate)**num_payments - 1)
    
    return monthly_payment

# Function to create amortization schedule
def create_amortization_schedule(principal, annual_rate, years):
    """Create detailed payment schedule."""
    monthly_payment = calculate_monthly_payment(principal, annual_rate, years)
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    payment_numbers = []
    payment_amounts = []
    principal_payments = []
    interest_payments = []
    remaining_balances = []
    
    remaining_balance = principal
    
    for payment_num in range(1, num_payments + 1):
        interest_payment = remaining_balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance = remaining_balance - principal_payment
        
        payment_numbers.append(payment_num)
        payment_amounts.append(monthly_payment)
        interest_payments.append(interest_payment)
        principal_payments.append(principal_payment)
        remaining_balances.append(max(0, remaining_balance))
    
    schedule = pd.DataFrame({
        'Payment_Number': payment_numbers,
        'Payment_Amount': payment_amounts,
        'Principal_Payment': principal_payments,
        'Interest_Payment': interest_payments,
        'Remaining_Balance': remaining_balances
    })
    
    return schedule

# Main calculation (runs when button is clicked or inputs change)
if calculate_button or True:  # Auto-calculate on input change
    
    # Calculate monthly payment
    monthly_payment = calculate_monthly_payment(loan_principal, annual_rate, loan_years)
    
    # Generate amortization schedule
    schedule = create_amortization_schedule(loan_principal, annual_rate, loan_years)
    
    # Calculate summary statistics
    total_payments = monthly_payment * loan_years * 12
    total_interest = total_payments - loan_principal
    
    # Display key metrics at the top
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Monthly Payment", f"${monthly_payment:,.2f}")
    
    with col2:
        st.metric("Total Paid", f"${total_payments:,.2f}")
    
    with col3:
        st.metric("Total Interest", f"${total_interest:,.2f}")
    
    with col4:
        interest_percentage = (total_interest / loan_principal) * 100
        st.metric("Interest/Principal", f"{interest_percentage:.1f}%")
    
    st.markdown("---")
    
    # Create interactive charts using Plotly
    st.subheader("📊 Cash Flow Visualization")
    
    # Create subplot with 2 charts
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Principal vs Interest Payment Over Time", "Remaining Loan Balance"),
        vertical_spacing=0.12,
        row_heights=[0.5, 0.5]
    )
    
    # Chart 1: Principal vs Interest
    fig.add_trace(
        go.Scatter(
            x=schedule['Payment_Number'],
            y=schedule['Principal_Payment'],
            name='Principal Payment',
            line=dict(color='#2E7D32', width=2),
            fill='tonexty',
            hovertemplate='Payment #%{x}<br>Principal: $%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=schedule['Payment_Number'],
            y=schedule['Interest_Payment'],
            name='Interest Payment',
            line=dict(color='#C62828', width=2),
            fill='tozeroy',
            hovertemplate='Payment #%{x}<br>Interest: $%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Chart 2: Remaining Balance
    fig.add_trace(
        go.Scatter(
            x=schedule['Payment_Number'],
            y=schedule['Remaining_Balance'],
            name='Remaining Balance',
            line=dict(color='#1565C0', width=3),
            fill='tozeroy',
            hovertemplate='Payment #%{x}<br>Balance: $%{y:,.2f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_xaxes(title_text="Payment Number (Month)", row=1, col=1)
    fig.update_xaxes(title_text="Payment Number (Month)", row=2, col=1)
    fig.update_yaxes(title_text="Payment Amount ($)", row=1, col=1)
    fig.update_yaxes(title_text="Remaining Balance ($)", row=2, col=1)
    
    fig.update_layout(
        height=700,
        showlegend=True,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Amortization Schedule Table
    st.markdown("---")
    st.subheader("📋 Amortization Schedule")
    
    # Format the dataframe for display
    display_schedule = schedule.copy()
    display_schedule['Payment_Amount'] = display_schedule['Payment_Amount'].apply(lambda x: f"${x:,.2f}")
    display_schedule['Principal_Payment'] = display_schedule['Principal_Payment'].apply(lambda x: f"${x:,.2f}")
    display_schedule['Interest_Payment'] = display_schedule['Interest_Payment'].apply(lambda x: f"${x:,.2f}")
    display_schedule['Remaining_Balance'] = display_schedule['Remaining_Balance'].apply(lambda x: f"${x:,.2f}")
    
    # Rename columns for better display
    display_schedule.columns = ['Payment Number', 'Payment Amount', 'Principal Payment', 
                                 'Interest Payment', 'Remaining Balance']
    
    # Display options
    col1, col2 = st.columns([1, 3])
    
    with col1:
        view_option = st.radio(
            "View:",
            ["First 12 Months", "Last 12 Months", "Full Schedule", "Every 12th Payment"],
            help="Choose which payments to display"
        )
    
    # Display based on selection
    if view_option == "First 12 Months":
        st.dataframe(display_schedule.head(12), use_container_width=True, hide_index=True)
    elif view_option == "Last 12 Months":
        st.dataframe(display_schedule.tail(12), use_container_width=True, hide_index=True)
    elif view_option == "Every 12th Payment":
        st.dataframe(display_schedule[::12], use_container_width=True, hide_index=True)
    else:
        st.dataframe(display_schedule, use_container_width=True, hide_index=True, height=400)
    
    # Download options
    st.markdown("---")
    st.subheader("💾 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Convert to CSV for download
        csv = schedule.to_csv(index=False)
        st.download_button(
            label="📥 Download Schedule (CSV)",
            data=csv,
            file_name=f"mortgage_schedule_{loan_principal}_{annual_rate}_{loan_years}y.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Create summary for download
        summary = pd.DataFrame({
            'Metric': ['Loan Amount', 'Interest Rate', 'Loan Term', 'Monthly Payment', 
                      'Total Paid', 'Total Interest', 'Interest/Principal Ratio'],
            'Value': [f"${loan_principal:,.2f}", f"{annual_rate}%", f"{loan_years} years",
                     f"${monthly_payment:,.2f}", f"${total_payments:,.2f}", 
                     f"${total_interest:,.2f}", f"{interest_percentage:.1f}%"]
        })
        
        csv_summary = summary.to_csv(index=False)
        st.download_button(
            label="📥 Download Summary (CSV)",
            data=csv_summary,
            file_name=f"mortgage_summary_{loan_principal}_{annual_rate}_{loan_years}y.csv",
            mime="text/csv",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
    <p>💡 <strong>Tip:</strong> Adjust the loan parameters in the sidebar to see how they affect your payments.</p>
    <p style='font-size: 0.9em;'>Built with Streamlit • For educational purposes</p>
    </div>
    """,
    unsafe_allow_html=True
)