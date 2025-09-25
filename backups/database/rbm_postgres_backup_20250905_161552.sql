--
-- PostgreSQL database dump
--

\restrict kq2gIdYZSHNa38fGX960WXQwNgdGCtggXUkYlpQ7H5UAGZKFEtbQv011KKRlTsd

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2025-09-05 16:15:52

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE IF EXISTS rbm_tender_app;
--
-- TOC entry 5266 (class 1262 OID 16388)
-- Name: rbm_tender_app; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE rbm_tender_app WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_Australia.1252';


ALTER DATABASE rbm_tender_app OWNER TO postgres;

\unrestrict kq2gIdYZSHNa38fGX960WXQwNgdGCtggXUkYlpQ7H5UAGZKFEtbQv011KKRlTsd
\connect rbm_tender_app
\restrict kq2gIdYZSHNa38fGX960WXQwNgdGCtggXUkYlpQ7H5UAGZKFEtbQv011KKRlTsd

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 882 (class 1247 OID 16390)
-- Name: activitystatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.activitystatus AS ENUM (
    'PENDING',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED',
    'SCHEDULED'
);


ALTER TYPE public.activitystatus OWNER TO postgres;

--
-- TOC entry 885 (class 1247 OID 16402)
-- Name: activitytype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.activitytype AS ENUM (
    'CALL',
    'EMAIL',
    'MEETING',
    'NOTE',
    'TASK',
    'DEAL_UPDATE',
    'QUOTE_SENT',
    'FOLLOW_UP',
    'OTHER'
);


ALTER TYPE public.activitytype OWNER TO postgres;

--
-- TOC entry 888 (class 1247 OID 16422)
-- Name: australianstate; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.australianstate AS ENUM (
    'NSW',
    'VIC',
    'QLD',
    'WA',
    'SA',
    'TAS',
    'NT',
    'ACT'
);


ALTER TYPE public.australianstate OWNER TO postgres;

--
-- TOC entry 891 (class 1247 OID 16440)
-- Name: calldirection; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.calldirection AS ENUM (
    'INBOUND',
    'OUTBOUND'
);


ALTER TYPE public.calldirection OWNER TO postgres;

--
-- TOC entry 894 (class 1247 OID 16446)
-- Name: calloutcome; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.calloutcome AS ENUM (
    'CONNECTED',
    'LEFT_MESSAGE',
    'NO_ANSWER',
    'BUSY',
    'WRONG_NUMBER',
    'SCHEDULED_CALLBACK'
);


ALTER TYPE public.calloutcome OWNER TO postgres;

--
-- TOC entry 897 (class 1247 OID 16460)
-- Name: dealstage; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.dealstage AS ENUM (
    'SALES_LEAD',
    'TENDER',
    'PROPOSAL',
    'NEGOTIATION',
    'WON',
    'LOST',
    'ABANDONED'
);


ALTER TYPE public.dealstage OWNER TO postgres;

--
-- TOC entry 900 (class 1247 OID 16476)
-- Name: dealtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.dealtype AS ENUM (
    'HVAC',
    'PLUMBING',
    'HYDRONIC_HEATING',
    'DATA_CENTRES',
    'MERCHANT',
    'WHOLESALER',
    'OEM'
);


ALTER TYPE public.dealtype OWNER TO postgres;

--
-- TOC entry 903 (class 1247 OID 16492)
-- Name: emaildirection; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.emaildirection AS ENUM (
    'SENT',
    'RECEIVED'
);


ALTER TYPE public.emaildirection OWNER TO postgres;

--
-- TOC entry 906 (class 1247 OID 16498)
-- Name: meetingtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.meetingtype AS ENUM (
    'IN_PERSON',
    'PHONE',
    'VIDEO',
    'SITE_VISIT',
    'PRESENTATION',
    'TECHNICAL_REVIEW'
);


ALTER TYPE public.meetingtype OWNER TO postgres;

--
-- TOC entry 909 (class 1247 OID 16512)
-- Name: notetype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.notetype AS ENUM (
    'GENERAL',
    'TECHNICAL',
    'COMMERCIAL',
    'FOLLOW_UP',
    'INTERNAL'
);


ALTER TYPE public.notetype OWNER TO postgres;

--
-- TOC entry 912 (class 1247 OID 16524)
-- Name: taskpriority; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.taskpriority AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'URGENT'
);


ALTER TYPE public.taskpriority OWNER TO postgres;

--
-- TOC entry 915 (class 1247 OID 16534)
-- Name: taskstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.taskstatus AS ENUM (
    'PENDING',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED',
    'DEFERRED'
);


ALTER TYPE public.taskstatus OWNER TO postgres;

--
-- TOC entry 918 (class 1247 OID 16546)
-- Name: tasktype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tasktype AS ENUM (
    'CALL',
    'EMAIL',
    'MEETING',
    'FOLLOW_UP',
    'QUOTE_PREPARATION',
    'PROPOSAL',
    'CONTRACT_REVIEW',
    'SITE_VISIT',
    'TECHNICAL_REVIEW',
    'OTHER'
);


ALTER TYPE public.tasktype OWNER TO postgres;

--
-- TOC entry 921 (class 1247 OID 16568)
-- Name: userrole; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'SALES',
    'MANAGER',
    'VIEWER'
);


ALTER TYPE public.userrole OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 217 (class 1259 OID 16577)
-- Name: activities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activities (
    title character varying(200) NOT NULL,
    description text,
    activity_type public.activitytype NOT NULL,
    status public.activitystatus NOT NULL,
    scheduled_date timestamp without time zone,
    completed_date timestamp without time zone,
    duration_minutes integer,
    user_id integer NOT NULL,
    company_id integer,
    contact_id integer,
    deal_id integer,
    is_private boolean NOT NULL,
    tags character varying(500),
    outcome character varying(200),
    next_action character varying(500),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.activities OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16582)
-- Name: activities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activities_id_seq OWNER TO postgres;

--
-- TOC entry 5267 (class 0 OID 0)
-- Dependencies: 218
-- Name: activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activities_id_seq OWNED BY public.activities.id;


--
-- TOC entry 219 (class 1259 OID 16583)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16586)
-- Name: calls; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.calls (
    activity_id integer NOT NULL,
    phone_number character varying(30) NOT NULL,
    direction public.calldirection NOT NULL,
    outcome public.calloutcome NOT NULL,
    duration_seconds integer,
    call_notes text,
    follow_up_required boolean NOT NULL,
    follow_up_date timestamp without time zone,
    call_recording_url character varying(500),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.calls OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16591)
-- Name: calls_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.calls_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.calls_id_seq OWNER TO postgres;

--
-- TOC entry 5268 (class 0 OID 0)
-- Dependencies: 221
-- Name: calls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.calls_id_seq OWNED BY public.calls.id;


--
-- TOC entry 222 (class 1259 OID 16592)
-- Name: companies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.companies (
    company_name character varying(120) NOT NULL,
    phone_number character varying(30),
    domain character varying(100),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.companies OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16595)
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.companies_id_seq OWNER TO postgres;

--
-- TOC entry 5269 (class 0 OID 0)
-- Dependencies: 223
-- Name: companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.companies_id_seq OWNED BY public.companies.id;


--
-- TOC entry 224 (class 1259 OID 16596)
-- Name: contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contacts (
    name character varying(120) NOT NULL,
    email character varying(120) NOT NULL,
    phone_number character varying(30),
    mobile_number character varying(30),
    "position" character varying(120),
    department character varying(100),
    is_primary boolean NOT NULL,
    is_active boolean NOT NULL,
    notes character varying(500),
    company_id integer NOT NULL,
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.contacts OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16601)
-- Name: contacts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.contacts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.contacts_id_seq OWNER TO postgres;

--
-- TOC entry 5270 (class 0 OID 0)
-- Dependencies: 225
-- Name: contacts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.contacts_id_seq OWNED BY public.contacts.id;


--
-- TOC entry 226 (class 1259 OID 16602)
-- Name: deal_companies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deal_companies (
    deal_id integer NOT NULL,
    company_id integer NOT NULL
);


ALTER TABLE public.deal_companies OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16605)
-- Name: deal_contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deal_contacts (
    deal_id integer NOT NULL,
    contact_id integer NOT NULL
);


ALTER TABLE public.deal_contacts OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16608)
-- Name: deals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deals (
    project_name character varying(200) NOT NULL,
    stage public.dealstage NOT NULL,
    deal_type public.dealtype NOT NULL,
    state public.australianstate NOT NULL,
    total_amount numeric(10,2),
    description text,
    expected_close_date timestamp without time zone,
    probability numeric(5,2),
    is_active boolean NOT NULL,
    notes text,
    owner_id integer NOT NULL,
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT check_deal_probability CHECK (((probability >= (0)::numeric) AND (probability <= (100)::numeric)))
);


ALTER TABLE public.deals OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16614)
-- Name: deals_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.deals_id_seq OWNER TO postgres;

--
-- TOC entry 5271 (class 0 OID 0)
-- Dependencies: 229
-- Name: deals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.deals_id_seq OWNED BY public.deals.id;


--
-- TOC entry 230 (class 1259 OID 16615)
-- Name: discounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.discounts (
    code character varying(10) NOT NULL,
    percentage numeric(5,2) NOT NULL,
    description character varying(200),
    is_active boolean NOT NULL,
    valid_from timestamp without time zone,
    valid_until timestamp without time zone,
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT check_discount_percentage CHECK (((percentage >= (0)::numeric) AND (percentage <= (100)::numeric)))
);


ALTER TABLE public.discounts OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16619)
-- Name: discounts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.discounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.discounts_id_seq OWNER TO postgres;

--
-- TOC entry 5272 (class 0 OID 0)
-- Dependencies: 231
-- Name: discounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.discounts_id_seq OWNED BY public.discounts.id;


--
-- TOC entry 232 (class 1259 OID 16620)
-- Name: emails; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.emails (
    activity_id integer NOT NULL,
    subject character varying(500) NOT NULL,
    direction public.emaildirection NOT NULL,
    sender_email character varying(200) NOT NULL,
    recipient_email character varying(200) NOT NULL,
    email_body text,
    has_attachments boolean NOT NULL,
    attachment_count integer,
    is_read boolean NOT NULL,
    is_replied boolean NOT NULL,
    email_thread_id character varying(200),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.emails OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 16625)
-- Name: emails_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.emails_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.emails_id_seq OWNER TO postgres;

--
-- TOC entry 5273 (class 0 OID 0)
-- Dependencies: 233
-- Name: emails_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.emails_id_seq OWNED BY public.emails.id;


--
-- TOC entry 234 (class 1259 OID 16626)
-- Name: meetings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.meetings (
    activity_id integer NOT NULL,
    meeting_type public.meetingtype NOT NULL,
    location character varying(200),
    meeting_notes text,
    attendees text,
    agenda text,
    action_items text,
    meeting_url character varying(500),
    follow_up_required boolean NOT NULL,
    follow_up_date timestamp without time zone,
    follow_up_notes text,
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.meetings OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 16631)
-- Name: meetings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.meetings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.meetings_id_seq OWNER TO postgres;

--
-- TOC entry 5274 (class 0 OID 0)
-- Dependencies: 235
-- Name: meetings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.meetings_id_seq OWNED BY public.meetings.id;


--
-- TOC entry 236 (class 1259 OID 16632)
-- Name: notes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notes (
    activity_id integer NOT NULL,
    note_type public.notetype NOT NULL,
    content text NOT NULL,
    is_internal boolean NOT NULL,
    is_important boolean NOT NULL,
    tags character varying(500),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.notes OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 16637)
-- Name: notes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notes_id_seq OWNER TO postgres;

--
-- TOC entry 5275 (class 0 OID 0)
-- Dependencies: 237
-- Name: notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notes_id_seq OWNED BY public.notes.id;


--
-- TOC entry 238 (class 1259 OID 16638)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    sku character varying(80) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    unit_price numeric(10,2) NOT NULL,
    category character varying(100),
    series character varying(100),
    item_no character varying(100),
    list_price_2025 numeric(10,2),
    discount_code character varying(10),
    nett_buy_price_gst numeric(10,2),
    brand character varying(100),
    model_number character varying(100),
    weight_kg numeric(8,3),
    dimensions character varying(100),
    is_active boolean NOT NULL,
    stock_quantity integer,
    reorder_level integer,
    lead_time_days integer,
    notes text,
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT check_product_lead_time CHECK ((lead_time_days >= 0)),
    CONSTRAINT check_product_list_price CHECK ((list_price_2025 >= (0)::numeric)),
    CONSTRAINT check_product_nett_price CHECK ((nett_buy_price_gst >= (0)::numeric)),
    CONSTRAINT check_product_reorder_level CHECK ((reorder_level >= 0)),
    CONSTRAINT check_product_stock_quantity CHECK ((stock_quantity >= 0)),
    CONSTRAINT check_product_unit_price CHECK ((unit_price >= (0)::numeric))
);


ALTER TABLE public.products OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 16649)
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO postgres;

--
-- TOC entry 5276 (class 0 OID 0)
-- Dependencies: 239
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- TOC entry 240 (class 1259 OID 16650)
-- Name: quote_line_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quote_line_items (
    option_id integer NOT NULL,
    product_id integer,
    quantity integer NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    notes text,
    discount numeric(5,2) NOT NULL,
    display_order integer NOT NULL,
    custom_sku character varying(80),
    custom_name character varying(200),
    custom_description text,
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT check_line_item_discount CHECK (((discount >= (0)::numeric) AND (discount <= (100)::numeric))),
    CONSTRAINT check_line_item_quantity CHECK ((quantity > 0)),
    CONSTRAINT check_line_item_unit_price CHECK ((unit_price >= (0)::numeric))
);


ALTER TABLE public.quote_line_items OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 16658)
-- Name: quote_line_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quote_line_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quote_line_items_id_seq OWNER TO postgres;

--
-- TOC entry 5277 (class 0 OID 0)
-- Dependencies: 241
-- Name: quote_line_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quote_line_items_id_seq OWNED BY public.quote_line_items.id;


--
-- TOC entry 242 (class 1259 OID 16659)
-- Name: quote_options; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quote_options (
    quote_id integer NOT NULL,
    name character varying(120) NOT NULL,
    freight_charge numeric(10,2) NOT NULL,
    lead_time_value character varying(20),
    lead_time_unit character varying(10),
    is_ex_stock_brisbane boolean,
    description text,
    is_recommended boolean,
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.quote_options OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 16664)
-- Name: quote_options_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quote_options_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quote_options_id_seq OWNER TO postgres;

--
-- TOC entry 5278 (class 0 OID 0)
-- Dependencies: 243
-- Name: quote_options_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quote_options_id_seq OWNED BY public.quote_options.id;


--
-- TOC entry 244 (class 1259 OID 16665)
-- Name: quote_recipients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quote_recipients (
    deal_id integer NOT NULL,
    company_id integer NOT NULL,
    contact_person character varying(120),
    delivery_method character varying(50),
    special_instructions text,
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.quote_recipients OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 16670)
-- Name: quote_recipients_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quote_recipients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quote_recipients_id_seq OWNER TO postgres;

--
-- TOC entry 5279 (class 0 OID 0)
-- Dependencies: 245
-- Name: quote_recipients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quote_recipients_id_seq OWNED BY public.quote_recipients.id;


--
-- TOC entry 246 (class 1259 OID 16671)
-- Name: quote_snapshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quote_snapshots (
    id integer NOT NULL,
    quote_option_id integer NOT NULL,
    version_number integer DEFAULT 1 NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_by_id integer,
    deleted_at timestamp without time zone,
    deleted_by_id integer,
    is_deleted boolean DEFAULT false,
    rendered_html text,
    snapshot_metadata text
);


ALTER TABLE public.quote_snapshots OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 16680)
-- Name: quote_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quote_snapshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quote_snapshots_id_seq OWNER TO postgres;

--
-- TOC entry 5280 (class 0 OID 0)
-- Dependencies: 247
-- Name: quote_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quote_snapshots_id_seq OWNED BY public.quote_snapshots.id;


--
-- TOC entry 248 (class 1259 OID 16681)
-- Name: quotes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotes (
    recipient_id integer NOT NULL,
    revision integer NOT NULL,
    notes text,
    created_at timestamp without time zone,
    valid_until timestamp without time zone,
    status character varying(20),
    total_discount numeric(5,2),
    id integer NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.quotes OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 16686)
-- Name: quotes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quotes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quotes_id_seq OWNER TO postgres;

--
-- TOC entry 5281 (class 0 OID 0)
-- Dependencies: 249
-- Name: quotes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quotes_id_seq OWNED BY public.quotes.id;


--
-- TOC entry 250 (class 1259 OID 16687)
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    title character varying(200) NOT NULL,
    description text,
    task_type public.tasktype NOT NULL,
    priority public.taskpriority NOT NULL,
    status public.taskstatus NOT NULL,
    due_date timestamp without time zone NOT NULL,
    start_date timestamp without time zone,
    completed_date timestamp without time zone,
    estimated_hours integer,
    actual_hours integer,
    assigned_to_id integer NOT NULL,
    created_by_id integer NOT NULL,
    company_id integer,
    contact_id integer,
    deal_id integer,
    is_recurring boolean NOT NULL,
    recurrence_pattern character varying(100),
    recurrence_interval integer,
    parent_task_id integer,
    tags character varying(500),
    notes text,
    completion_notes text,
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 16692)
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tasks_id_seq OWNER TO postgres;

--
-- TOC entry 5282 (class 0 OID 0)
-- Dependencies: 251
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- TOC entry 252 (class 1259 OID 16693)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(256) NOT NULL,
    first_name character varying(50),
    last_name character varying(50),
    phone_number character varying(20),
    role public.userrole NOT NULL,
    is_active boolean,
    last_login timestamp without time zone,
    force_password_change boolean,
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    two_factor_enabled boolean DEFAULT false,
    two_factor_secret character varying(32),
    backup_codes character varying(500)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 253 (class 1259 OID 16698)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 5283 (class 0 OID 0)
-- Dependencies: 253
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4876 (class 2604 OID 17033)
-- Name: activities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities ALTER COLUMN id SET DEFAULT nextval('public.activities_id_seq'::regclass);


--
-- TOC entry 4877 (class 2604 OID 17034)
-- Name: calls id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calls ALTER COLUMN id SET DEFAULT nextval('public.calls_id_seq'::regclass);


--
-- TOC entry 4878 (class 2604 OID 17035)
-- Name: companies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies ALTER COLUMN id SET DEFAULT nextval('public.companies_id_seq'::regclass);


--
-- TOC entry 4879 (class 2604 OID 17036)
-- Name: contacts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contacts ALTER COLUMN id SET DEFAULT nextval('public.contacts_id_seq'::regclass);


--
-- TOC entry 4880 (class 2604 OID 17037)
-- Name: deals id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deals ALTER COLUMN id SET DEFAULT nextval('public.deals_id_seq'::regclass);


--
-- TOC entry 4881 (class 2604 OID 17038)
-- Name: discounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.discounts ALTER COLUMN id SET DEFAULT nextval('public.discounts_id_seq'::regclass);


--
-- TOC entry 4882 (class 2604 OID 17039)
-- Name: emails id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emails ALTER COLUMN id SET DEFAULT nextval('public.emails_id_seq'::regclass);


--
-- TOC entry 4883 (class 2604 OID 17040)
-- Name: meetings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.meetings ALTER COLUMN id SET DEFAULT nextval('public.meetings_id_seq'::regclass);


--
-- TOC entry 4884 (class 2604 OID 17041)
-- Name: notes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes ALTER COLUMN id SET DEFAULT nextval('public.notes_id_seq'::regclass);


--
-- TOC entry 4885 (class 2604 OID 17042)
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- TOC entry 4886 (class 2604 OID 17043)
-- Name: quote_line_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_line_items ALTER COLUMN id SET DEFAULT nextval('public.quote_line_items_id_seq'::regclass);


--
-- TOC entry 4887 (class 2604 OID 17044)
-- Name: quote_options id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_options ALTER COLUMN id SET DEFAULT nextval('public.quote_options_id_seq'::regclass);


--
-- TOC entry 4888 (class 2604 OID 17045)
-- Name: quote_recipients id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_recipients ALTER COLUMN id SET DEFAULT nextval('public.quote_recipients_id_seq'::regclass);


--
-- TOC entry 4889 (class 2604 OID 17046)
-- Name: quote_snapshots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_snapshots ALTER COLUMN id SET DEFAULT nextval('public.quote_snapshots_id_seq'::regclass);


--
-- TOC entry 4894 (class 2604 OID 17047)
-- Name: quotes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quotes ALTER COLUMN id SET DEFAULT nextval('public.quotes_id_seq'::regclass);


--
-- TOC entry 4895 (class 2604 OID 17048)
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- TOC entry 4896 (class 2604 OID 17049)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 5224 (class 0 OID 16577)
-- Dependencies: 217
-- Data for Name: activities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.activities (title, description, activity_type, status, scheduled_date, completed_date, duration_minutes, user_id, company_id, contact_id, deal_id, is_private, tags, outcome, next_action, id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5226 (class 0 OID 16583)
-- Dependencies: 219
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
add_lead_time_fields_simple
\.


--
-- TOC entry 5227 (class 0 OID 16586)
-- Dependencies: 220
-- Data for Name: calls; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.calls (activity_id, phone_number, direction, outcome, duration_seconds, call_notes, follow_up_required, follow_up_date, call_recording_url, id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5229 (class 0 OID 16592)
-- Dependencies: 222
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.companies (company_name, phone_number, domain, id, created_at, updated_at) FROM stdin;
Drillcut	+61383019999	@drillcut.com.au	1	2025-08-06 06:03:30.967099	2025-08-06 06:03:30.967104
\.


--
-- TOC entry 5231 (class 0 OID 16596)
-- Dependencies: 224
-- Data for Name: contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contacts (name, email, phone_number, mobile_number, "position", department, is_primary, is_active, notes, company_id, id, created_at, updated_at) FROM stdin;
Gary Shirreff	Gary.Shirreff@drillcut.com.au		+61437009205	 Key Account Manager	\N	f	t		1	1	2025-08-06 06:04:24.909973	2025-08-06 06:04:24.909975
\.


--
-- TOC entry 5233 (class 0 OID 16602)
-- Dependencies: 226
-- Data for Name: deal_companies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.deal_companies (deal_id, company_id) FROM stdin;
1	1
\.


--
-- TOC entry 5234 (class 0 OID 16605)
-- Dependencies: 227
-- Data for Name: deal_contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.deal_contacts (deal_id, contact_id) FROM stdin;
1	1
\.


--
-- TOC entry 5235 (class 0 OID 16608)
-- Dependencies: 228
-- Data for Name: deals; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.deals (project_name, stage, deal_type, state, total_amount, description, expected_close_date, probability, is_active, notes, owner_id, id, created_at, updated_at) FROM stdin;
Lorimer St	TENDER	PLUMBING	VIC	16328.40	\N	\N	0.00	t	\N	2	1	2025-08-06 06:04:44.997623	2025-09-05 05:46:08.763529
\.


--
-- TOC entry 5237 (class 0 OID 16615)
-- Dependencies: 230
-- Data for Name: discounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.discounts (code, percentage, description, is_active, valid_from, valid_until, id, created_at, updated_at) FROM stdin;
P1	70.00	\N	t	\N	\N	1	2025-08-06 05:53:44.066461	2025-08-06 05:53:44.066464
H1	70.00	\N	t	\N	\N	2	2025-08-06 05:53:44.069933	2025-08-06 05:53:44.069941
C1	70.00	\N	t	\N	\N	3	2025-08-06 05:53:44.071171	2025-08-06 05:53:44.071174
WC1	40.00	\N	t	\N	\N	4	2025-08-06 05:53:44.071778	2025-08-06 05:53:44.07178
ZIL1	30.00	\N	t	\N	\N	5	2025-08-06 05:53:44.072354	2025-08-06 05:53:44.072356
\.


--
-- TOC entry 5239 (class 0 OID 16620)
-- Dependencies: 232
-- Data for Name: emails; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.emails (activity_id, subject, direction, sender_email, recipient_email, email_body, has_attachments, attachment_count, is_read, is_replied, email_thread_id, id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5241 (class 0 OID 16626)
-- Dependencies: 234
-- Data for Name: meetings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.meetings (activity_id, meeting_type, location, meeting_notes, attendees, agenda, action_items, meeting_url, follow_up_required, follow_up_date, follow_up_notes, id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5243 (class 0 OID 16632)
-- Dependencies: 236
-- Data for Name: notes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notes (activity_id, note_type, content, is_internal, is_important, tags, id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5245 (class 0 OID 16638)
-- Dependencies: 238
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (sku, name, description, unit_price, category, series, item_no, list_price_2025, discount_code, nett_buy_price_gst, brand, model_number, weight_kg, dimensions, is_active, stock_quantity, reorder_level, lead_time_days, notes, id, created_at, updated_at) FROM stdin;
25810400	Rinox Plus M G1/2" (15mm) Pressure reducing valve	\N	96.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	1	2025-08-06 05:53:44.080558	2025-08-06 05:53:44.08056
25810500	Rinox Plus M G3/4" (20mm) Pressure reducing valve	\N	96.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	2	2025-08-06 05:53:44.082058	2025-08-06 05:53:44.08206
25810600	Rinox Plus M G1" (25mm) Pressure reducing valve	\N	240.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	3	2025-08-06 05:53:44.08261	2025-08-06 05:53:44.082611
25810700	Rinox Plus M G1 1/4" (32mm) Pressure reducing valve	\N	340.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	4	2025-08-06 05:53:44.083138	2025-08-06 05:53:44.08314
25810800	Rinox Plus M G1 1/2" (40mm) Pressure reducing valve	\N	448.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	5	2025-08-06 05:53:44.083681	2025-08-06 05:53:44.083683
25810900	Rinox Plus M G2" (50mm) Pressure reducing valve	\N	766.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	6	2025-08-06 05:53:44.084237	2025-08-06 05:53:44.084239
25810490	Rinox Plus SmartM G1/2" (15mm) Pressure reducing valve with calibration knob	\N	200.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	7	2025-08-06 05:53:44.084828	2025-08-06 05:53:44.08483
25810590	Rinox Plus SmartM G3/4" (20mm) Pressure reducing valve with calibration knob	\N	222.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	8	2025-08-06 05:53:44.085384	2025-08-06 05:53:44.085386
25810690	Rinox Plus SmartM G1" (25mm) Pressure reducing valve with calibration knob	\N	403.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	9	2025-08-06 05:53:44.085976	2025-08-06 05:53:44.085978
25810790	Rinox Plus SmartM G1 1/4" (32mm) Pressure reducing valve with calibration knob	\N	578.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	10	2025-08-06 05:53:44.086726	2025-08-06 05:53:44.086728
25810890	Rinox Plus SmartM G1 1/2" (40mm) Pressure reducing valve with calibration knob	\N	727.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	11	2025-08-06 05:53:44.087332	2025-08-06 05:53:44.087334
25810990	Rinox Plus SmartM G2" (50mm) Pressure reducing valve with calibration knob	\N	1165.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	12	2025-08-06 05:53:44.087882	2025-08-06 05:53:44.087884
870470	Rinox Due FF G1/2" (15mm) Pressure Reducing Valve PN25	\N	142.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	13	2025-08-06 05:53:44.088421	2025-08-06 05:53:44.088423
870570	Rinox Due FF G3/4" (20mm) Pressure Reducing Valve PN25	\N	142.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	14	2025-08-06 05:53:44.088923	2025-08-06 05:53:44.088925
870670	Rinox Due FF G1" (25mm) Pressure Reducing Valve PN25	\N	262.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	15	2025-08-06 05:53:44.089447	2025-08-06 05:53:44.089448
870770	Rinox Due FF G1 1/4" (32mm) Pressure Reducing Valve PN25	\N	325.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	16	2025-08-06 05:53:44.089946	2025-08-06 05:53:44.089948
870870	Rinox Due FF G1 1/2" (40mm)Pressure Reducing Valve PN25	\N	366.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	17	2025-08-06 05:53:44.090446	2025-08-06 05:53:44.090448
870970	Rinox Due FF G2" (50mm) Pressure Reducing Valve PN25	\N	422.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	18	2025-08-06 05:53:44.090924	2025-08-06 05:53:44.090926
510495	Rinox First G1/2" (15mm) Pressure reducing valve FF PN40	\N	362.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	19	2025-08-06 05:53:44.091418	2025-08-06 05:53:44.09142
510595	Rinox First G3/4" (20mm) Pressure reducing valve FF PN40	\N	379.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	20	2025-08-06 05:53:44.091893	2025-08-06 05:53:44.091894
510695	Rinox First G1" (25mm) Pressure reducing valve FF PN40	\N	455.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	21	2025-08-06 05:53:44.092418	2025-08-06 05:53:44.092419
510795	Rinox First G1 1/4" (32mm) Pressure reducing valve FF PN40	\N	698.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	22	2025-08-06 05:53:44.092916	2025-08-06 05:53:44.092917
510895	Rinox First G1 1/2" (40mm) Pressure reducing valve FF PN40	\N	885.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	23	2025-08-06 05:53:44.093414	2025-08-06 05:53:44.093416
510995	Rinox First G2" (50mm) Pressure reducing valve FF PN40	\N	1122.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	24	2025-08-06 05:53:44.093906	2025-08-06 05:53:44.093908
T08T121-15HP	T08 15mm High Performance Tempering Valve With Unions	\N	166.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	25	2025-08-06 05:53:44.094418	2025-08-06 05:53:44.09442
T08T191-20HP	T08 20mm High Performance Tempering Valve With Unions	\N	190.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	26	2025-08-06 05:53:44.094937	2025-08-06 05:53:44.094939
T08T191-15TMV	RBM T08 20mm Tempering valve with 15mm TMV Isolation Elbows	\N	289.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	27	2025-08-06 05:53:44.095431	2025-08-06 05:53:44.095433
T08T191-20TMV	RBM T08 20mm Tempering valve with 20mm TMV Isolation Elbows	\N	299.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	28	2025-08-06 05:53:44.095962	2025-08-06 05:53:44.095964
T16T121-15TMV	T16 Thermostatic Mixing Valve 15mm high performance	\N	430.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	29	2025-08-06 05:53:44.097018	2025-08-06 05:53:44.09702
T16T191-20TMV	T16 Thermostatic Mixing Valve 20mm high performance	\N	520.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	30	2025-08-06 05:53:44.097565	2025-08-06 05:53:44.097567
RBMS-21-0014	RBM T16 15mm PrePlumbed TMV in Cabinet (3 pipe)	\N	1035.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	31	2025-08-06 05:53:44.098076	2025-08-06 05:53:44.098078
RBMS-21-0015	RBM T16 15mm PrePlumbed TMV in Cabinet with CW bypass (4 pipe)	\N	1240.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	32	2025-08-06 05:53:44.09863	2025-08-06 05:53:44.098632
RBMS-21-0019	RBM T16 20mm PrePlumbed TMV in Cabinet (3 pipe)	\N	1095.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	33	2025-08-06 05:53:44.099148	2025-08-06 05:53:44.099149
RBMS-21-0020	RBM T16 20mm PrePlumbed TMV in Cabinet with CW bypass (4 pipe)	\N	1310.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	34	2025-08-06 05:53:44.099621	2025-08-06 05:53:44.099623
RBMS-21-0059	Stainless Steel Cabinet with removeable face to suit tempering and TMV	\N	550.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	35	2025-08-06 05:53:44.100144	2025-08-06 05:53:44.100146
T55T122-15TF	RBM T55 Health 15mm TMV with Thermal Flush	\N	670.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	36	2025-08-06 05:53:44.10066	2025-08-06 05:53:44.100662
T55T192-20TF	RBM T55 Health 20mm TMV with Thermal Flush	\N	760.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	37	2025-08-06 05:53:44.101177	2025-08-06 05:53:44.101179
PT-L0101	FPV Frost Protection Valve G1/2" (15mm) to suit solar hot water systems	\N	190.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	38	2025-08-06 05:53:44.10179	2025-08-06 05:53:44.101792
D06T120G-EV	D06 Thermosyphon Arrestor Valve G3/4" + G1/2"	\N	210.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	39	2025-08-06 05:53:44.102721	2025-08-06 05:53:44.102723
RBM-AF0012MF	ActivFlo SOLO 1/2" shower water conditioner (3-14 lpm)	\N	0.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	40	2025-08-06 05:53:44.103536	2025-08-06 05:53:44.103538
RBM-AF0038MF	ActivFlo NANO 3/8" commercial water conditioner (1-11 lpm)	\N	299.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	41	2025-08-06 05:53:44.104151	2025-08-06 05:53:44.104153
RBM-AF0015C	15mm ActivFlo hard water conditioner compression fittings (3-22 lpm)	\N	639.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	42	2025-08-06 05:53:44.104683	2025-08-06 05:53:44.104685
RBM-AF0020C	20mm ActivFlo hard water conditioner compression fittings (22-45 lpm)	\N	749.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	43	2025-08-06 05:53:44.105213	2025-08-06 05:53:44.105215
RBM-AF0025C	25mm ActivFlo hard water conditioner compression fittings (45-74 lpm)	\N	1059.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	44	2025-08-06 05:53:44.105695	2025-08-06 05:53:44.105697
RBM-AF0012T	1/2" (15mm) ActivFlo hard water conditioner BSP Threaded (3-22 lpm)	\N	639.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	45	2025-08-06 05:53:44.106283	2025-08-06 05:53:44.106285
RBM-AF0034T	3/4" (20mm) ActivFlo hard water conditioner BSP Threaded (22-45 lpm)	\N	749.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	46	2025-08-06 05:53:44.106788	2025-08-06 05:53:44.10679
RBM-AF0100T	1" (25mm) ActivFlo hard water conditioner BSP Threaded (45-74 lpm)	\N	1059.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	47	2025-08-06 05:53:44.107271	2025-08-06 05:53:44.107273
RBM-AF0114T	1-1/4" (32mm) ActivFlo hard water conditioner BSP Threaded (75-117 lpm)	\N	2400.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	48	2025-08-06 05:53:44.107772	2025-08-06 05:53:44.107775
RBM-AF0112T	1-1/2" (40mm) ActivFlo hard water conditioner BSP Threaded (117-170 lpm)	\N	3010.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	49	2025-08-06 05:53:44.108236	2025-08-06 05:53:44.108238
RBM-AF0200T	2" (50mm) ActivFlo hard water conditioner BSP Threaded (170-264 lpm)	\N	3600.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	50	2025-08-06 05:53:44.108671	2025-08-06 05:53:44.108673
RBM-AF0212T	2-1/2" (65mm) ActivFlo hard water conditioner BSP Threaded (264-330 lpm)	\N	7600.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	51	2025-08-06 05:53:44.10912	2025-08-06 05:53:44.109121
RBM-AF0300F	80mm Flanged ActivFlo hard water conditioner (360-685 lpm)	\N	11920.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	52	2025-08-06 05:53:44.109573	2025-08-06 05:53:44.109575
RBM-AF0400F	100mm Flanged ActivFlo hard water conditioner (685-1,260 lpm)	\N	13980.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	53	2025-08-06 05:53:44.110814	2025-08-06 05:53:44.110815
RBM-AF0500F	125mm Flanged ActivFlo hard water conditioner (1,260-1,823 lpm)	\N	0.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	54	2025-08-06 05:53:44.111661	2025-08-06 05:53:44.111662
RBM-AF0600F	150mm Flanged ActivFlo hard water conditioner (1,823-3,500 lpm)	\N	0.00	\N	\N	\N	\N	WC1	\N	\N	\N	\N	\N	t	0	0	0	\N	55	2025-08-06 05:53:44.11219	2025-08-06 05:53:44.112192
8167003	Complete cartridge for diaphragm pressure reducing valve 1/2" & 3/4"	\N	75.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	56	2025-08-06 05:53:44.112711	2025-08-06 05:53:44.112713
8201003	Complete cartridge for diaphragm pressure reducing valve 1"	\N	151.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	57	2025-08-06 05:53:44.113222	2025-08-06 05:53:44.113224
8202003	Complete cartridge for diaphragm pressure reducing valve 1 1/4"	\N	192.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	58	2025-08-06 05:53:44.113721	2025-08-06 05:53:44.113723
8203003	Complete cartridge for diaphragm pressure reducing valve 1 1/2" & 2"	\N	206.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	59	2025-08-06 05:53:44.114204	2025-08-06 05:53:44.114206
1213005	1/4" Radial pressure gauge 0-16Bar 50mm to suit Rinox PRVs	\N	37.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	60	2025-08-06 05:53:44.114688	2025-08-06 05:53:44.11469
RBMS-21-0052	RBM T16 TMV 5-Year service & maintenance kit	\N	199.00	\N	\N	\N	\N	P1	\N	\N	\N	\N	\N	t	0	0	0	\N	61	2025-08-06 05:53:44.115188	2025-08-06 05:53:44.11519
6190450	Balancing Valve Threaded G1/2" (15mm)	\N	188.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	62	2025-08-06 05:53:44.115663	2025-08-06 05:53:44.115664
6190550	Balancing Valve Threaded G3/4" (20mm)	\N	196.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	63	2025-08-06 05:53:44.116129	2025-08-06 05:53:44.116131
6190650	Balancing Valve Threaded G1" (25mm)	\N	242.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	64	2025-08-06 05:53:44.116616	2025-08-06 05:53:44.116617
6190750	Balancing Valve Threaded G1 1/4" (32mm)	\N	272.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	65	2025-08-06 05:53:44.117085	2025-08-06 05:53:44.117087
6190850	Balancing Valve Threaded G1 1/2" (40mm)	\N	411.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	66	2025-08-06 05:53:44.117551	2025-08-06 05:53:44.117553
6190950	Balancing Valve Threaded G2" (50mm)	\N	627.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	67	2025-08-06 05:53:44.118043	2025-08-06 05:53:44.118045
6191060	Balancing Valve Flanged DN65	\N	1605.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	68	2025-08-06 05:53:44.118551	2025-08-06 05:53:44.118553
6191160	Balancing Valve Flanged DN80	\N	1845.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	69	2025-08-06 05:53:44.119084	2025-08-06 05:53:44.119086
6191360	Balancing Valve Flanged DN100	\N	3220.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	70	2025-08-06 05:53:44.119652	2025-08-06 05:53:44.119655
6191460	Balancing Valve Flanged DN125	\N	4615.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	71	2025-08-06 05:53:44.120283	2025-08-06 05:53:44.120285
6191560	Balancing Valve Flanged DN150	\N	5899.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	72	2025-08-06 05:53:44.120934	2025-08-06 05:53:44.120936
6191760	Balancing Valve Flanged DN200	\N	15129.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	73	2025-08-06 05:53:44.121816	2025-08-06 05:53:44.121819
6191960	Balancing Valve Flanged DN250	\N	20888.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	74	2025-08-06 05:53:44.122627	2025-08-06 05:53:44.122629
6210150	Pair of pressure plugs - Brass to suit threaded valves	\N	81.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	75	2025-08-06 05:53:44.123448	2025-08-06 05:53:44.12345
28740450	Pressure independent control valve. provided with pressure plugs 57-575 L/H G1/2" (15mm)	\N	449.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	76	2025-08-06 05:53:44.124198	2025-08-06 05:53:44.1242
28740460	Pressure independent control valve. provided with pressure plugs 64-1110 L/H G1/2" (15mm)	\N	449.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	77	2025-08-06 05:53:44.124923	2025-08-06 05:53:44.124926
28740550	Pressure independent control valve. provided with pressure plugs 57-575 L/H G3/4" (20mm)	\N	509.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	78	2025-08-06 05:53:44.125678	2025-08-06 05:53:44.12568
28740560	Pressure independent control valve. provided with pressure plugs 64-1110 L/H G3/4" (20mm)	\N	526.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	79	2025-08-06 05:53:44.126406	2025-08-06 05:53:44.126409
28740650	Pressure independent control valve. provided with pressure plugs 57-575 L/H G1" (25mm)	\N	643.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	80	2025-08-06 05:53:44.127119	2025-08-06 05:53:44.127122
28740660	Pressure independent control valve. provided with pressure plugs 64-1110 L/H G1" (25mm)	\N	643.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	81	2025-08-06 05:53:44.127859	2025-08-06 05:53:44.127862
37170500	Fan Coil Unit (FCU) Valve Combi Kit G3/4" (20mm) 400 lph	\N	1250.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	82	2025-08-06 05:53:44.128569	2025-08-06 05:53:44.128572
37170510	Fan Coil Unit (FCU) Valve Combi Kit G3/4" (20mm) 700 lph	\N	1250.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	83	2025-08-06 05:53:44.129306	2025-08-06 05:53:44.129308
37170520	Fan Coil Unit (FCU) Valve Combi Kit G3/4" (20mm) 1300 lph	\N	1250.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	84	2025-08-06 05:53:44.130027	2025-08-06 05:53:44.130029
35660000	Portable Electronic Differential Pressure and Flow Measuring Commissioning Unit	\N	19530.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	85	2025-08-06 05:53:44.130706	2025-08-06 05:53:44.130709
9320100	Pair of needle adaptors for pressure measurements	\N	78.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	86	2025-08-06 05:53:44.131434	2025-08-06 05:53:44.131436
28820002	Electromechanical actuator 24V AC	\N	550.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	87	2025-08-06 05:53:44.132103	2025-08-06 05:53:44.132105
28820012	Electromechanical actuator 110-230V AC	\N	650.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	88	2025-08-06 05:53:44.13277	2025-08-06 05:53:44.132773
28820022	Electromechanical actuator 24V AC 3 Points	\N	540.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	89	2025-08-06 05:53:44.133436	2025-08-06 05:53:44.133439
28810012	Thermo-electric actuator 24V AC/DC	\N	125.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	90	2025-08-06 05:53:44.134099	2025-08-06 05:53:44.134101
28810022	Thermo-electric actuator 230V AC	\N	125.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	91	2025-08-06 05:53:44.135191	2025-08-06 05:53:44.135193
29440002	Thermo-electric actuator 230V AC	\N	135.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	92	2025-08-06 05:53:44.135942	2025-08-06 05:53:44.135945
29440012	Thermo-electric actuator 24V AC	\N	135.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	93	2025-08-06 05:53:44.136782	2025-08-06 05:53:44.136785
29440042	Thermo-electric actuator 230V AC+Microswitch	\N	195.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	94	2025-08-06 05:53:44.137532	2025-08-06 05:53:44.137534
29440052	Thermo-electric actuator 24V AC+Microswitch	\N	195.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	95	2025-08-06 05:53:44.138368	2025-08-06 05:53:44.13837
CDP-15	15L SS HVAC Chemical Dosing Pot	\N	1499.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	96	2025-08-06 05:53:44.139032	2025-08-06 05:53:44.139034
RBMS-21-0006	Automatic Filling Kit G1/2" (15mm)	\N	610.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	97	2025-08-06 05:53:44.139628	2025-08-06 05:53:44.139631
RBMS-21-0012	Buffer tank gauge and airvent kit	\N	1108.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	98	2025-08-06 05:53:44.140223	2025-08-06 05:53:44.140225
28740410	Pressure Control Valve G1/2" (15mm) 17-210kPa, 0.100-0.412 m3/hr	\N	475.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	99	2025-08-06 05:53:44.140799	2025-08-06 05:53:44.140802
28740420	Pressure Control Valve G1/2" (15mm) 17-210kPa, 0.157-0.609 m3/hr	\N	475.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	100	2025-08-06 05:53:44.141372	2025-08-06 05:53:44.141373
28740430	Pressure Control Valve G1/2" (15mm) 17-200kPa, 0.275-0.825 m3/hr	\N	475.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	101	2025-08-06 05:53:44.1419	2025-08-06 05:53:44.141902
28740440	Pressure Control Valve G1/2" (15mm) 30-400kPa, 0.406-1.270 m3/hr	\N	475.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	102	2025-08-06 05:53:44.142407	2025-08-06 05:53:44.142409
28740510	Pressure Control Valve G3/4" (20mm) 17-210kPa, 0.100-0.412 m3/hr	\N	505.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	103	2025-08-06 05:53:44.143078	2025-08-06 05:53:44.14308
28740520	Pressure Control Valve G3/4" (20mm) 17-210kPa, 0.157-0.609 m3/hr	\N	505.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	104	2025-08-06 05:53:44.143773	2025-08-06 05:53:44.143774
28740530	Pressure Control Valve G3/4" (20mm) 17-200kPa, 0.275-0.825 m3/hr	\N	505.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	105	2025-08-06 05:53:44.14431	2025-08-06 05:53:44.144312
28740540	Pressure Control Valve G3/4" (20mm) 30-400kPa, 0.406-1.270 m3/hr	\N	505.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	106	2025-08-06 05:53:44.144853	2025-08-06 05:53:44.144855
28740610	Pressure Control Valve G1" (25mm) 17-210kPa, 0.100-0.412 m3/hr	\N	532.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	107	2025-08-06 05:53:44.145357	2025-08-06 05:53:44.145359
28740620	Pressure Control Valve G1" (25mm) 17-210kPa, 0.157-0.609 m3/hr	\N	532.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	108	2025-08-06 05:53:44.145868	2025-08-06 05:53:44.14587
28740630	Pressure Control Valve G1" (25mm) 17-200kPa, 0.275-0.825 m3/hr	\N	532.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	109	2025-08-06 05:53:44.14636	2025-08-06 05:53:44.146362
28740640	Pressure Control Valve G1" (25mm) 30-400kPa, 0.406-1.270 m3/hr	\N	532.00	\N	\N	\N	\N	H1	\N	\N	\N	\N	\N	t	0	0	0	\N	110	2025-08-06 05:53:44.146854	2025-08-06 05:53:44.146856
38412010	Kilma Futura SP20 1200x800 High efficiency insulation panel for dry installations	\N	275.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	111	2025-08-06 05:53:44.147335	2025-08-06 05:53:44.147337
38412510	Kilma Futura SP25 1200x800 High efficiency insulation panel for dry installations	\N	245.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	112	2025-08-06 05:53:44.147814	2025-08-06 05:53:44.147815
38413310	Kilma Futura SP33 1200x800 High efficiency insulation panel for dry installations	\N	268.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	113	2025-08-06 05:53:44.1483	2025-08-06 05:53:44.148302
38414810	Kilma Futura SP48 1200x800 High efficiency insulation panel for dry installations	\N	330.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	114	2025-08-06 05:53:44.14885	2025-08-06 05:53:44.148852
25171612	Hi-Performance Plus 16X2,0 R120M 4-Layer Polyethylene pipe	\N	3.70	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	115	2025-08-06 05:53:44.149318	2025-08-06 05:53:44.14932
25171602	Hi-Performance Plus 16X2,0 R240M 4-Layer Polyethylene pipe	\N	3.60	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	116	2025-08-06 05:53:44.149815	2025-08-06 05:53:44.149816
25171622	Hi-Performance Plus 16X2,0 R600M 4-Layer Polyethylene pipe	\N	3.50	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	117	2025-08-06 05:53:44.150289	2025-08-06 05:53:44.150291
25171712	Hi-Performance Plus 17X2,0 R120M 4-Layer Polyethylene pipe	\N	4.10	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	118	2025-08-06 05:53:44.150863	2025-08-06 05:53:44.150865
25171702	Hi-Performance Plus 17X2,0 R240M 4-Layer Polyethylene pipe	\N	3.90	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	119	2025-08-06 05:53:44.151739	2025-08-06 05:53:44.151741
25171722	Hi-Performance Plus 17X2,0 R600M 4-Layer Polyethylene pipe	\N	3.70	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	120	2025-08-06 05:53:44.152293	2025-08-06 05:53:44.152294
25172002	Hi-Performance Plus 20X2,0 R240M 4-Layer Polyethylene pipe	\N	5.90	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	121	2025-08-06 05:53:44.152855	2025-08-06 05:53:44.152857
25172032	Hi-Performance Plus 20X2,0 R500M 4-Layer Polyethylene pipe	\N	5.70	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	122	2025-08-06 05:53:44.153478	2025-08-06 05:53:44.15348
4640802	Kilma Flex Pe-Xc pipe 8x1 1,000m roll	\N	2.90	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	123	2025-08-06 05:53:44.153992	2025-08-06 05:53:44.153994
4641002	Kilma Flex Pe-Xc pipe 10x,12 1,000m roll	\N	3.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	124	2025-08-06 05:53:44.154442	2025-08-06 05:53:44.154444
4641602	Kilma Flex Pe-Xc pipe 16x2 120m roll	\N	4.55	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	125	2025-08-06 05:53:44.154876	2025-08-06 05:53:44.154877
4641612	Kilma Flex Pe-Xc pipe 16x2 240m roll	\N	4.55	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	126	2025-08-06 05:53:44.155357	2025-08-06 05:53:44.155359
4641622	Kilma Flex Pe-Xc pipe 16x2 600m roll	\N	4.55	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	127	2025-08-06 05:53:44.155824	2025-08-06 05:53:44.155826
4641712	Kilma Flex Pe-Xc pipe 17x2 120m roll	\N	5.90	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	128	2025-08-06 05:53:44.156288	2025-08-06 05:53:44.15629
4641702	Kilma Flex Pe-Xc pipe 17x2 240m roll	\N	5.80	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	129	2025-08-06 05:53:44.156771	2025-08-06 05:53:44.156773
4641722	Kilma Flex Pe-Xc pipe 17x2 600m roll	\N	5.70	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	130	2025-08-06 05:53:44.157285	2025-08-06 05:53:44.157287
4642002	Kilma Flex Pe-Xc pipe 20x2 240m roll	\N	8.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	131	2025-08-06 05:53:44.15805	2025-08-06 05:53:44.158052
4642032	Kilma Flex Pe-Xc pipe 20x2 500m roll	\N	7.90	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	132	2025-08-06 05:53:44.158637	2025-08-06 05:53:44.158638
4642502	Kilma Flex Pe-Xc pipe 25x2,3 240m roll	\N	14.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	133	2025-08-06 05:53:44.159199	2025-08-06 05:53:44.1592
4642522	Kilma Flex Pe-Xc pipe 25x2,3 310m roll	\N	13.90	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	134	2025-08-06 05:53:44.159721	2025-08-06 05:53:44.159723
20091702	Kilma Flex Pe-Xa pipe 17x2 600m roll	\N	6.55	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	135	2025-08-06 05:53:44.160246	2025-08-06 05:53:44.160248
20092002	Kilma Flex Pe-Xa pipe 20x2 500m roll	\N	7.95	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	136	2025-08-06 05:53:44.160809	2025-08-06 05:53:44.160811
14841622	Kilma Flex Pe-RT pipe 16x2 120m roll	\N	3.50	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	137	2025-08-06 05:53:44.161365	2025-08-06 05:53:44.161367
14841632	Kilma Flex Pe-RT pipe 16x2 240m roll	\N	3.50	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	138	2025-08-06 05:53:44.161891	2025-08-06 05:53:44.161893
14841602	Kilma Flex Pe-RT pipe 16x2 600m roll	\N	3.50	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	139	2025-08-06 05:53:44.162456	2025-08-06 05:53:44.162458
14841712	Kilma Flex Pe-RT pipe 17x2 120m roll	\N	4.50	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	140	2025-08-06 05:53:44.163032	2025-08-06 05:53:44.163034
14841702	Kilma Flex Pe-RT pipe 17x2 240m roll	\N	4.40	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	141	2025-08-06 05:53:44.16369	2025-08-06 05:53:44.163692
14841722	Kilma Flex Pe-RT pipe 17x2 600m roll	\N	4.30	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	142	2025-08-06 05:53:44.164431	2025-08-06 05:53:44.164433
14842002	Kilma Flex Pe-RT pipe 20x2 500m roll	\N	6.10	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	143	2025-08-06 05:53:44.165158	2025-08-06 05:53:44.16516
14842512	Kilma Flex Pe-RT pipe 25x2,3 240m roll	\N	8.60	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	144	2025-08-06 05:53:44.165884	2025-08-06 05:53:44.165886
14842502	Kilma Flex Pe-RT pipe 25x2,3 310m roll	\N	8.50	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	145	2025-08-06 05:53:44.166592	2025-08-06 05:53:44.166595
13611000	Kilma Super-Strong Position Board 1300 x 800 x 33	\N	57.50	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	146	2025-08-06 05:53:44.167281	2025-08-06 05:53:44.167284
13611800	Kilma Super-Strong Position Board 1300 x 800 x 40	\N	65.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	147	2025-08-06 05:53:44.168279	2025-08-06 05:53:44.168282
13612800	Kilma Super-Strong Position Board 1300 x 800 x 50	\N	82.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	148	2025-08-06 05:53:44.169088	2025-08-06 05:53:44.16909
13614200	Kilma Super-Strong Position Board 1300 x 800 x 65	\N	94.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	149	2025-08-06 05:53:44.169828	2025-08-06 05:53:44.169831
13615000	Kilma Super-Strong Position Board 1300 x 800 x 73	\N	108.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	150	2025-08-06 05:53:44.17088	2025-08-06 05:53:44.170883
4690002	Fastener clip tool	\N	1890.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	151	2025-08-06 05:53:44.171612	2025-08-06 05:53:44.171614
6031812	90deg Bend former to suit 17mm pipe	\N	7.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	152	2025-08-06 05:53:44.172542	2025-08-06 05:53:44.172545
6032012	90deg Bend former to suit 20mm pipe	\N	9.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	153	2025-08-06 05:53:44.173265	2025-08-06 05:53:44.173267
6032502	90deg Bend former to suit 25mm pipe	\N	10.50	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	154	2025-08-06 05:53:44.174195	2025-08-06 05:53:44.174197
6670000	Universal unwinder for pipe coils	\N	1335.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	155	2025-08-06 05:53:44.174863	2025-08-06 05:53:44.174865
19381300	Kilma Bull Insulating Panel SP13 1200X800X33	\N	70.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	156	2025-08-06 05:53:44.175465	2025-08-06 05:53:44.175467
19382500	Kilma Bull Insulating Panel SP25 1200X800X45	\N	80.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	157	2025-08-06 05:53:44.176087	2025-08-06 05:53:44.176089
19384000	Kilma Bull Insulating Panel SP40 1200X800X60	\N	98.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	158	2025-08-06 05:53:44.176695	2025-08-06 05:53:44.176697
19782002	Kilma Roll Rolled Panel SP20MM	\N	76.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	159	2025-08-06 05:53:44.177343	2025-08-06 05:53:44.177345
19783002	Kilma Roll Rolled Panel SP30MM	\N	88.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	160	2025-08-06 05:53:44.177966	2025-08-06 05:53:44.177968
19784002	Kilma Roll Rolled Panel SP40MM	\N	102.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	161	2025-08-06 05:53:44.178564	2025-08-06 05:53:44.178567
19785002	Kilma Roll Rolled Panel SP50MM	\N	118.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	162	2025-08-06 05:53:44.179159	2025-08-06 05:53:44.179162
14100620	Polymer compact manifold kit 1" (25mm) 2+2 Ways	\N	659.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	163	2025-08-06 05:53:44.179727	2025-08-06 05:53:44.17973
14110620	Polymer compact manifold kit 1" (25mm) 3+3 Ways	\N	748.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	164	2025-08-06 05:53:44.180346	2025-08-06 05:53:44.180348
14120620	Polymer compact manifold kit 1" (25mm) 4+4 Ways	\N	820.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	165	2025-08-06 05:53:44.180958	2025-08-06 05:53:44.18096
14130620	Polymer compact manifold kit 1" (25mm) 5+5 Ways	\N	899.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	166	2025-08-06 05:53:44.181543	2025-08-06 05:53:44.181545
14140620	Polymer compact manifold kit 1" (25mm) 6+6 Ways	\N	969.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	167	2025-08-06 05:53:44.182152	2025-08-06 05:53:44.182153
14150620	Polymer compact manifold kit 1" (25mm) 7+7 Ways	\N	1058.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	168	2025-08-06 05:53:44.18284	2025-08-06 05:53:44.182842
14160620	Polymer compact manifold kit 1" (25mm) 8+8 Ways	\N	1140.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	169	2025-08-06 05:53:44.183514	2025-08-06 05:53:44.183516
14170620	Polymer compact manifold kit 1" (25mm) 9+9 Ways	\N	1215.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	170	2025-08-06 05:53:44.184216	2025-08-06 05:53:44.184218
14180620	Polymer compact manifold kit 1" (25mm) 10+10 Ways	\N	1298.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	171	2025-08-06 05:53:44.185073	2025-08-06 05:53:44.185076
14190620	Polymer compact manifold kit 1" (25mm) 11+11 Ways	\N	1598.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	172	2025-08-06 05:53:44.185838	2025-08-06 05:53:44.18584
14200620	Polymer compact manifold kit 1" (25mm) 12+12 Ways	\N	1664.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	173	2025-08-06 05:53:44.186663	2025-08-06 05:53:44.186666
14201320	Polymer compact manifold kit 1" (25mm) 13+13 Ways	\N	1756.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	174	2025-08-06 05:53:44.187595	2025-08-06 05:53:44.187598
14201420	Polymer compact manifold kit 1" (25mm) 14+14 Ways	\N	1855.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	175	2025-08-06 05:53:44.188372	2025-08-06 05:53:44.188375
2171660	Polymer Fitting *16x2	\N	17.10	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	176	2025-08-06 05:53:44.189061	2025-08-06 05:53:44.189063
10020640	Polymer compact manifold kit 2+2 way with anti-condensation jacket 1"	\N	1066.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	177	2025-08-06 05:53:44.189716	2025-08-06 05:53:44.189718
10030640	Polymer compact manifold kit 3+3 way with anti-condensation jacket 1"	\N	1178.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	178	2025-08-06 05:53:44.190405	2025-08-06 05:53:44.190407
10040640	Polymer compact manifold kit 4+4 way with anti-condensation jacket 1"	\N	1282.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	179	2025-08-06 05:53:44.19107	2025-08-06 05:53:44.191083
10050640	Polymer compact manifold kit 5+5 way with anti-condensation jacket 1"	\N	1412.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	180	2025-08-06 05:53:44.191753	2025-08-06 05:53:44.191755
10060640	Polymer compact manifold kit 6+6 way with anti-condensation jacket 1"	\N	1520.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	181	2025-08-06 05:53:44.192423	2025-08-06 05:53:44.192426
10070640	Polymer compact manifold kit 7+7 way with anti-condensation jacket 1"	\N	1625.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	182	2025-08-06 05:53:44.193077	2025-08-06 05:53:44.193079
10080640	Polymer compact manifold kit 8+8 way with anti-condensation jacket 1"	\N	1740.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	183	2025-08-06 05:53:44.193722	2025-08-06 05:53:44.193724
10090640	Polymer compact manifold kit 9+9 way with anti-condensation jacket 1"	\N	1840.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	184	2025-08-06 05:53:44.1944	2025-08-06 05:53:44.194403
10100640	Polymer compact manifold kit 10+10 way with anti-condensation jacket 1"	\N	1920.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	185	2025-08-06 05:53:44.195067	2025-08-06 05:53:44.19507
10110640	Polymer compact manifold kit 11+11 way with anti-condensation jacket 1"	\N	2088.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	186	2025-08-06 05:53:44.195742	2025-08-06 05:53:44.195744
10120640	Polymer compact manifold kit 12+12 way with anti-condensation jacket 1"	\N	2590.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	187	2025-08-06 05:53:44.196384	2025-08-06 05:53:44.196387
10130640	Polymer compact manifold kit 13+13 way with anti-condensation jacket 1"	\N	2729.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	188	2025-08-06 05:53:44.197081	2025-08-06 05:53:44.197083
2171700	Compression Fitting for Polyethylene pipe 17x2	\N	18.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	189	2025-08-06 05:53:44.198071	2025-08-06 05:53:44.198074
2172000	Compression Fitting for Polyethylene pipe 20x2	\N	24.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	190	2025-08-06 05:53:44.198758	2025-08-06 05:53:44.19876
2241600	Compression Fitting for Multilayer pipe 16x2	\N	17.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	191	2025-08-06 05:53:44.199395	2025-08-06 05:53:44.199397
2242000	Compression Fitting for Multilayer pipe 20x2	\N	22.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	192	2025-08-06 05:53:44.200045	2025-08-06 05:53:44.200047
2080510	Flow metre G3/4" 0 to 5 lpm	\N	120.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	193	2025-08-06 05:53:44.200683	2025-08-06 05:53:44.200685
RBMS-21-0066	Adjustable manifold stand	\N	530.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	194	2025-08-06 05:53:44.201495	2025-08-06 05:53:44.201497
3060002	Thermo-Electrical Servo Motor 230V AC	\N	89.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	195	2025-08-06 05:53:44.202251	2025-08-06 05:53:44.202254
3060012	Thermo-Electrical Servo Motor 24V AC	\N	89.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	196	2025-08-06 05:53:44.2032	2025-08-06 05:53:44.203203
3060042	Thermo-Electrical Servo Motor 230V AC with Auxillary Microswitch	\N	109.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	197	2025-08-06 05:53:44.204041	2025-08-06 05:53:44.204042
3060052	Thermo-Electrical Servo Motor 24V AC with Auxillary Microswitch	\N	109.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	198	2025-08-06 05:53:44.204683	2025-08-06 05:53:44.204686
15310671	Kilma ECO-RF-AT Polymer fixed point mixing unit for high and low temp	\N	3090.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	199	2025-08-06 05:53:44.205441	2025-08-06 05:53:44.205444
15310651	Kilma ECO-RF Polymer fixed point mixing unit for low temp	\N	2620.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	200	2025-08-06 05:53:44.20612	2025-08-06 05:53:44.206122
35230651	Kilma ECOMIX RF50 series Fixed Point mixing unit	\N	2455.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	201	2025-08-06 05:53:44.206771	2025-08-06 05:53:44.206773
35230637	Kilma ECOMIX RF37 series Fixed Point mixing unit	\N	2099.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	202	2025-08-06 05:53:44.207412	2025-08-06 05:53:44.207414
31950602	Multimix booster unit DN25 2-Zones	\N	1740.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	203	2025-08-06 05:53:44.208033	2025-08-06 05:53:44.208035
31960602	Multimix booster unit DN25 3-Zones	\N	2230.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	204	2025-08-06 05:53:44.208687	2025-08-06 05:53:44.20869
31970602	RD Direct Booster Unit DN25	\N	1950.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	205	2025-08-06 05:53:44.209329	2025-08-06 05:53:44.209331
31980600	RF MIX B.T Mixing Unit - Low Temperature Fixed Point	\N	3420.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	206	2025-08-06 05:53:44.209978	2025-08-06 05:53:44.20998
31980610	RF MIX A.T Mixing Unit - High Temperature Fixed Point	\N	3860.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	207	2025-08-06 05:53:44.210611	2025-08-06 05:53:44.210614
31990602	RM MIX Mixing Unit DN25	\N	2320.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	208	2025-08-06 05:53:44.211241	2025-08-06 05:53:44.211243
32190702	Multimix S32 Hydraulic Separator 	\N	3140.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	209	2025-08-06 05:53:44.211867	2025-08-06 05:53:44.211869
32220702	Insulated pipe kit to connect Multimix 2-3 Ways	\N	855.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	210	2025-08-06 05:53:44.212487	2025-08-06 05:53:44.21249
3510490	Safety relief valve G1/2" (15mm) FF 6Bar	\N	39.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	262	2025-08-06 05:53:44.249802	2025-08-06 05:53:44.249804
32220712	Insulated pipe kit to connect Multimix 4-5 Ways	\N	970.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	211	2025-08-06 05:53:44.213112	2025-08-06 05:53:44.213115
32230702	Multimix C32 Zone Manifold 2 Ways	\N	2300.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	212	2025-08-06 05:53:44.213747	2025-08-06 05:53:44.213749
32240702	Multimix C32 Zone Manifold 3 Ways	\N	3090.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	213	2025-08-06 05:53:44.214351	2025-08-06 05:53:44.214353
32250702	Multimix C32 Zone Manifold 4 Ways	\N	4470.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	214	2025-08-06 05:53:44.21496	2025-08-06 05:53:44.214962
32260702	Multimix C32 Zone Manifold 5 Ways	\N	5820.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	215	2025-08-06 05:53:44.215586	2025-08-06 05:53:44.215588
32270002	Wall support kit for Multimix C32	\N	190.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	216	2025-08-06 05:53:44.216186	2025-08-06 05:53:44.216188
32280702	RD32 Direct Booster Unit DN32	\N	3226.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	217	2025-08-06 05:53:44.216773	2025-08-06 05:53:44.216775
32290702	RM MIX Mixing Unit DN32	\N	4145.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	218	2025-08-06 05:53:44.217397	2025-08-06 05:53:44.217398
32340602	RD25 Direct Booster Unit DN25 High Temp Unit	\N	2999.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	219	2025-08-06 05:53:44.218525	2025-08-06 05:53:44.218528
32350600	RF25 CONT B.T Mixing Unit - Low Temperature Fixed Point	\N	4290.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	220	2025-08-06 05:53:44.219269	2025-08-06 05:53:44.219272
32350610	RF25 CONT A.T Mixing Unit - High Temperature Fixed Point	\N	4650.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	221	2025-08-06 05:53:44.220163	2025-08-06 05:53:44.220166
32360602	RM25 Climatic Booster Unit	\N	3680.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	222	2025-08-06 05:53:44.221101	2025-08-06 05:53:44.221104
38560400	SmartFiller M with gauge automatic filling unit G1/2" (15mm) PN16	\N	223.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	223	2025-08-06 05:53:44.221731	2025-08-06 05:53:44.221733
38560490	SmartFiller M without gauge automatic filling unit G1/2" (15mm) PN16	\N	196.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	224	2025-08-06 05:53:44.222346	2025-08-06 05:53:44.222348
470610	Kombiluft Safety unit G1" 3Bar safety valve	\N	270.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	225	2025-08-06 05:53:44.222918	2025-08-06 05:53:44.222921
40930600	Zerofrost Antifreeze valve for heat pumps 1"	\N	599.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	226	2025-08-06 05:53:44.223571	2025-08-06 05:53:44.223573
40930700	Zerofrost Antifreeze valve for heat pumps 1-1/4"	\N	629.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	227	2025-08-06 05:53:44.22421	2025-08-06 05:53:44.224213
1240500	Differential Pressure Bypass Valve 20mm	\N	128.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	228	2025-08-06 05:53:44.224904	2025-08-06 05:53:44.224906
1240600	Differential Pressure Bypass Valve 25mm	\N	219.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	229	2025-08-06 05:53:44.225587	2025-08-06 05:53:44.225589
1240700	Differential Pressure Bypass Valve 32mm	\N	285.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	230	2025-08-06 05:53:44.226325	2025-08-06 05:53:44.226328
ZIL-1300000400	Zilmet Expansion Tank Cal-Pro 4 Litre - 5Bar max working pressure - preset 1.5Bar	\N	130.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	231	2025-08-06 05:53:44.227077	2025-08-06 05:53:44.22708
ZIL-1300000800	Zilmet Expansion Tank Cal-Pro 8 Litre - 5Bar max working pressure - preset 1.5Bar	\N	135.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	232	2025-08-06 05:53:44.227781	2025-08-06 05:53:44.227784
ZIL-1300001200	Zilmet Expansion Tank Cal-Pro 12 Litre - 4Bar max working pressure - preset 1.5Bar	\N	155.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	233	2025-08-06 05:53:44.228524	2025-08-06 05:53:44.228526
ZIL-1300001800	Zilmet Expansion Tank Cal-Pro 18 Litre - 4Bar max working pressure - preset 1.5Bar	\N	170.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	234	2025-08-06 05:53:44.229216	2025-08-06 05:53:44.229219
ZIL-1300002400	Zilmet Expansion Tank Cal-Pro 25 Litre - 4Bar max working pressure - preset 1.5Bar	\N	205.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	235	2025-08-06 05:53:44.229932	2025-08-06 05:53:44.229934
ZIL-1300003500	Zilmet Expansion Tank Cal-Pro 35 Litre - 4Bar max working pressure - preset 1.5Bar	\N	305.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	236	2025-08-06 05:53:44.230641	2025-08-06 05:53:44.230644
ZIL-1300003503	Zilmet Expansion Tank Cal-Pro 35 Litre with Feet - 4Bar max working pressure - preset 1.5Bar	\N	325.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	237	2025-08-06 05:53:44.231401	2025-08-06 05:53:44.231404
ZIL-1300005000	Zilmet Expansion Tank Cal-Pro 50 Litre - 4Bar max working pressure - preset 1.5Bar	\N	365.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	238	2025-08-06 05:53:44.232115	2025-08-06 05:53:44.232118
ZIL-1300005003	Zilmet Expansion Tank Cal-Pro 50 Litre with Feet - 4Bar max working pressure - preset 1.5Bar	\N	430.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	239	2025-08-06 05:53:44.232899	2025-08-06 05:53:44.232901
ZIL-1300008000	Zilmet Expansion Tank Cal-Pro 80 Litre - 6Bar max working pressure - preset 2Bar	\N	572.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	240	2025-08-06 05:53:44.23376	2025-08-06 05:53:44.233762
ZIL-1300010500	Zilmet Expansion Tank Cal-Pro 105 Litre - 6Bar max working pressure - preset 2Bar	\N	795.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	241	2025-08-06 05:53:44.234602	2025-08-06 05:53:44.234604
ZIL-1300015000	Zilmet Expansion Tank Cal-Pro 150 Litre - 6Bar max working pressure - preset 2Bar	\N	999.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	242	2025-08-06 05:53:44.235515	2025-08-06 05:53:44.235518
ZIL-1300020000	Zilmet Expansion Tank Cal-Pro 200 Litre - 6Bar max working pressure - preset 2.5Bar	\N	1295.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	243	2025-08-06 05:53:44.236537	2025-08-06 05:53:44.236543
ZIL-1300025000	Zilmet Expansion Tank Cal-Pro 250 Litre - 6Bar max working pressure - preset 2.5Bar	\N	1595.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	244	2025-08-06 05:53:44.237472	2025-08-06 05:53:44.237474
ZIL-1300030000	Zilmet Expansion Tank Cal-Pro 300 Litre - 6Bar max working pressure - preset 2.5Bar	\N	1915.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	245	2025-08-06 05:53:44.238404	2025-08-06 05:53:44.238407
ZIL-1300040000	Zilmet Expansion Tank Cal-Pro 400 Litre - 6Bar max working pressure - preset 2.5Bar	\N	2660.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	246	2025-08-06 05:53:44.239145	2025-08-06 05:53:44.239147
ZIL-1300050000	Zilmet Expansion Tank Cal-Pro 500 Litre - 6Bar max working pressure - preset 2.5Bar	\N	3350.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	247	2025-08-06 05:53:44.239851	2025-08-06 05:53:44.239854
ZIL-1300060000	Zilmet Expansion Tank Cal-Pro 600 Litre - 6Bar max working pressure - preset 2.5Bar	\N	4230.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	248	2025-08-06 05:53:44.240485	2025-08-06 05:53:44.240488
ZIL-1100002418	Zilmet Expansion Tank Ultra-Pro 24 Litre - 10Bar max working pressure - preset 1.5Bar	\N	180.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	249	2025-08-06 05:53:44.241131	2025-08-06 05:53:44.241133
ZIL-1100005004	Zilmet Expansion Tank Ultra-Pro 50 Litre - 10Bar max working pressure - preset 1.5Bar	\N	615.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	250	2025-08-06 05:53:44.24177	2025-08-06 05:53:44.241773
ZIL-1100010004	Zilmet Expansion Tank Ultra-Pro 100 Litre - 10Bar max working pressure - preset 1.5Bar	\N	960.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	251	2025-08-06 05:53:44.242433	2025-08-06 05:53:44.242436
ZIL-1100020004	Zilmet Expansion Tank Ultra-Pro 200 Litre - 10Bar max working pressure - preset 1.5Bar	\N	1850.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	252	2025-08-06 05:53:44.243111	2025-08-06 05:53:44.243114
ZIL-1100030004	Zilmet Expansion Tank Ultra-Pro 300 Litre - 10Bar max working pressure - preset 1.5Bar	\N	2225.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	253	2025-08-06 05:53:44.243766	2025-08-06 05:53:44.243768
ZIL-1100050004	Zilmet Expansion Tank Ultra-Pro 500 Litre - 10Bar max working pressure - preset 1.5Bar	\N	3520.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	254	2025-08-06 05:53:44.24446	2025-08-06 05:53:44.244462
ZIL-1100075056	Zilmet Expansion Tank Ultra-Pro 750 Litre - 10Bar max working pressure - preset 1.5Bar	\N	6299.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	255	2025-08-06 05:53:44.245119	2025-08-06 05:53:44.245121
ZIL-1100100055	Zilmet Expansion Tank Ultra-Pro 1,000 Litre - 10Bar max working pressure - preset 1.5Bar	\N	7980.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	256	2025-08-06 05:53:44.245787	2025-08-06 05:53:44.245789
RBMS-21-0017	Wall Bracket to suit Zilmet expansion vessels	\N	50.00	\N	\N	\N	\N	ZIL1	\N	\N	\N	\N	\N	t	0	0	0	\N	257	2025-08-06 05:53:44.24647	2025-08-06 05:53:44.246473
3510410	Safety relief valve G1/2" (15mm) FF 1.5Bar	\N	39.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	258	2025-08-06 05:53:44.247106	2025-08-06 05:53:44.247108
3510420	Safety relief valve G1/2" (15mm) FF 2Bar	\N	39.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	259	2025-08-06 05:53:44.247747	2025-08-06 05:53:44.247749
3510440	Safety relief valve G1/2" (15mm) FF 3Bar	\N	39.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	260	2025-08-06 05:53:44.248392	2025-08-06 05:53:44.248395
3510460	Safety relief valve G1/2" (15mm) FF 4Bar	\N	39.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	261	2025-08-06 05:53:44.249122	2025-08-06 05:53:44.249124
3510481	Safety relief valve G1/2" (15mm) FF 8Bar	\N	39.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	263	2025-08-06 05:53:44.250462	2025-08-06 05:53:44.250465
3510411	Safety relief valve G1/2" (15mm) FF 10Bar	\N	39.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	264	2025-08-06 05:53:44.251286	2025-08-06 05:53:44.251289
3510560	Safety relief valve G3/4" (20mm) FF 4Bar	\N	51.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	265	2025-08-06 05:53:44.252174	2025-08-06 05:53:44.252178
3510510	Safety relief valve G3/4" (20mm) FF 1.5Bar	\N	51.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	266	2025-08-06 05:53:44.253255	2025-08-06 05:53:44.253258
3510520	Safety relief valve G3/4" (20mm) FF 2Bar	\N	48.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	267	2025-08-06 05:53:44.25424	2025-08-06 05:53:44.254243
3510530	Safety relief valve G3/4" (20mm) FF 2.5Bar	\N	48.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	268	2025-08-06 05:53:44.255018	2025-08-06 05:53:44.255021
3510540	Safety relief valve G3/4" (20mm) FF 3Bar	\N	51.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	269	2025-08-06 05:53:44.255801	2025-08-06 05:53:44.255803
3510550	Safety relief valve G3/4" (20mm) FF 3.5Bar	\N	51.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	270	2025-08-06 05:53:44.25656	2025-08-06 05:53:44.256563
3510570	Safety relief valve G3/4" (20mm) FF 4.5Bar	\N	51.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	271	2025-08-06 05:53:44.25768	2025-08-06 05:53:44.257682
3510580	Safety relief valve G3/4" (20mm) FF 5Bar	\N	51.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	272	2025-08-06 05:53:44.258408	2025-08-06 05:53:44.258411
3510590	Safety relief valve G3/4" (20mm) FF 6Bar	\N	51.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	273	2025-08-06 05:53:44.259148	2025-08-06 05:53:44.259151
3510571	Safety relief valve G3/4" (20mm) FF 7Bar	\N	51.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	274	2025-08-06 05:53:44.259847	2025-08-06 05:53:44.259849
3510581	Safety relief valve G3/4" (20mm) FF 8Bar	\N	51.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	275	2025-08-06 05:53:44.260582	2025-08-06 05:53:44.260585
3510511	Safety relief valve G3/4" (20mm) FF 10Bar	\N	51.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	276	2025-08-06 05:53:44.261296	2025-08-06 05:53:44.261298
3530420	Safety relief valve G1/2" (15mm) FF 2Bar with pressure gauge	\N	86.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	277	2025-08-06 05:53:44.262006	2025-08-06 05:53:44.262009
3530440	Safety relief valve G1/2" (15mm) FF 3Bar with pressure gauge	\N	86.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	278	2025-08-06 05:53:44.262768	2025-08-06 05:53:44.262771
3530460	Safety relief valve G1/2" (15mm) FF 4Bar with pressure gauge	\N	86.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	279	2025-08-06 05:53:44.263501	2025-08-06 05:53:44.263504
3530470	Safety relief valve G1/2" (15mm) FF 4.5Bar with pressure gauge	\N	86.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	280	2025-08-06 05:53:44.264204	2025-08-06 05:53:44.264206
3530490	Safety relief valve G1/2" (15mm) FF 6Bar with pressure gauge	\N	86.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	281	2025-08-06 05:53:44.264943	2025-08-06 05:53:44.264945
3530481	Safety relief valve G1/2" (15mm) FF 8Bar with pressure gauge	\N	86.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	282	2025-08-06 05:53:44.265637	2025-08-06 05:53:44.265639
3530411	Safety relief valve G1/2" (15mm) FF 10Bar with pressure gauge	\N	86.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	283	2025-08-06 05:53:44.26632	2025-08-06 05:53:44.266322
3530510	Safety relief valve G3/4" (20mm) FF 1.5Bar with pressure gauge	\N	96.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	284	2025-08-06 05:53:44.267054	2025-08-06 05:53:44.267056
3530520	Safety relief valve G3/4" (20mm) FF 2Bar with pressure gauge	\N	96.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	285	2025-08-06 05:53:44.267814	2025-08-06 05:53:44.267817
3530530	Safety relief valve G3/4" (20mm) FF 2.5Bar with pressure gauge	\N	96.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	286	2025-08-06 05:53:44.268574	2025-08-06 05:53:44.268576
3530540	Safety relief valve G3/4" (20mm) FF 3Bar with pressure gauge	\N	96.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	287	2025-08-06 05:53:44.269392	2025-08-06 05:53:44.269395
3530550	Safety relief valve G3/4" (20mm) FF 3.5Bar with pressure gauge	\N	96.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	288	2025-08-06 05:53:44.270398	2025-08-06 05:53:44.270401
3530560	Safety relief valve G3/4" (20mm) FF 4Bar with pressure gauge	\N	96.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	289	2025-08-06 05:53:44.27119	2025-08-06 05:53:44.271192
3530570	Safety relief valve G3/4" (20mm) FF 4.5Bar with pressure gauge	\N	96.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	290	2025-08-06 05:53:44.271796	2025-08-06 05:53:44.271798
3530580	Safety relief valve G3/4" (20mm) FF 5Bar with pressure gauge	\N	96.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	291	2025-08-06 05:53:44.272445	2025-08-06 05:53:44.272447
3530590	Safety relief valve G3/4" (20mm) FF 6Bar with pressure gauge	\N	96.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	292	2025-08-06 05:53:44.273051	2025-08-06 05:53:44.273053
3530571	Safety relief valve G3/4" (20mm) FF 7Bar with pressure gauge	\N	96.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	293	2025-08-06 05:53:44.273798	2025-08-06 05:53:44.2738
3530581	Safety relief valve G3/4" (20mm) FF 8Bar with pressure gauge	\N	96.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	294	2025-08-06 05:53:44.274407	2025-08-06 05:53:44.274409
3530511	Safety relief valve G3/4" (20mm) FF 10Bar with pressure gauge	\N	96.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	295	2025-08-06 05:53:44.274977	2025-08-06 05:53:44.274979
38290370	Check Valve - 3/8"Fx3/8"M	\N	16.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	296	2025-08-06 05:53:44.275549	2025-08-06 05:53:44.275551
38290470	Check Valve - 3/8"Fx1/2"M	\N	20.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	297	2025-08-06 05:53:44.276127	2025-08-06 05:53:44.276129
380450	Check Valve-1/2"Fx1/2"M	\N	17.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	298	2025-08-06 05:53:44.276687	2025-08-06 05:53:44.276689
7910440	Miniluft CP Polymer automatic airvent 1/2"	\N	58.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	299	2025-08-06 05:53:44.277266	2025-08-06 05:53:44.277268
28270400	Miniluft Compact Airvent G1/2" 4Bar	\N	61.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	300	2025-08-06 05:53:44.277866	2025-08-06 05:53:44.277867
28280310	Miniluft High Performance Airvent G3/8" 6Bar	\N	71.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	301	2025-08-06 05:53:44.278442	2025-08-06 05:53:44.278444
28280400	Miniluft High Performance Airvent G1/2" 6Bar	\N	70.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	302	2025-08-06 05:53:44.279023	2025-08-06 05:53:44.279024
35740400	Miniluft High Performance Airvent G1/2" 8Bar	\N	87.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	303	2025-08-06 05:53:44.27959	2025-08-06 05:53:44.279592
28360400	Megaluft High Performance G1/2" 10Bar	\N	135.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	304	2025-08-06 05:53:44.280145	2025-08-06 05:53:44.280147
28300400	Airterm In-line deaerator 1/2"FF (15mm) 10 BAR	\N	410.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	305	2025-08-06 05:53:44.280756	2025-08-06 05:53:44.280758
28300500	Airterm In-line deaerator 3/4"FF (20mm) 10 BAR	\N	429.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	306	2025-08-06 05:53:44.281326	2025-08-06 05:53:44.281328
28300600	Airterm In-line deaerator 1"FF (25mm) 10 BAR	\N	437.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	307	2025-08-06 05:53:44.281964	2025-08-06 05:53:44.281967
28300700	Airterm In-line deaerator 1"1/4FF (32mm) 10 BAR	\N	562.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	308	2025-08-06 05:53:44.282551	2025-08-06 05:53:44.282553
28300800	Airterm In-line deaerator 1"1/2FF (40mm) 10 BAR	\N	758.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	309	2025-08-06 05:53:44.283133	2025-08-06 05:53:44.283135
28300900	Airterm In-line deaerator 2"FF (50mm) 10 BAR	\N	805.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	310	2025-08-06 05:53:44.284121	2025-08-06 05:53:44.284123
28300972P	Airterm flanged deaerator DN50 10 BAR	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	311	2025-08-06 05:53:44.285062	2025-08-06 05:53:44.285064
28301072P	Airterm flanged deaerator DN65 10 BAR	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	312	2025-08-06 05:53:44.28602	2025-08-06 05:53:44.286022
28301172P	Airterm flanged deaerator DN80 10 BAR	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	313	2025-08-06 05:53:44.287321	2025-08-06 05:53:44.287323
28301372P	Airterm flanged deaerator DN100 10 BAR	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	314	2025-08-06 05:53:44.288174	2025-08-06 05:53:44.288176
28301472P	Airterm flanged deaerator DN125 10 BAR	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	315	2025-08-06 05:53:44.288964	2025-08-06 05:53:44.288966
28301572P	Airterm flanged deaerator DN150 10 BAR	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	316	2025-08-06 05:53:44.289552	2025-08-06 05:53:44.289554
28290400	Dirterm Mechanical Dirt Separator G1/2" (15mm)	\N	347.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	317	2025-08-06 05:53:44.290102	2025-08-06 05:53:44.290103
28290500	Dirterm Mechanical Dirt Separator G3/4" (20mm)	\N	362.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	318	2025-08-06 05:53:44.29065	2025-08-06 05:53:44.290652
28290600	Dirterm Mechanical Dirt Separator G1" (25mm)	\N	370.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	319	2025-08-06 05:53:44.291473	2025-08-06 05:53:44.291476
28290700	Dirterm Mechanical Dirt Separator G1 1/4" (32mm)	\N	473.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	320	2025-08-06 05:53:44.292146	2025-08-06 05:53:44.292148
28290800	Dirterm Mechanical Dirt Separator G1 1/2" (40mm)	\N	621.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	321	2025-08-06 05:53:44.292706	2025-08-06 05:53:44.292708
28290900	Dirterm Mechanical Dirt Separator G2" (50mm)	\N	633.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	322	2025-08-06 05:53:44.293538	2025-08-06 05:53:44.29354
28290972P	Dirterm flanged deaerator DN50 10 BAR	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	323	2025-08-06 05:53:44.294299	2025-08-06 05:53:44.294302
28291072P	Dirterm flanged deaerator DN65 10 BAR	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	324	2025-08-06 05:53:44.295017	2025-08-06 05:53:44.295018
28291172P	Dirterm flanged deaerator DN80 10 BAR	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	325	2025-08-06 05:53:44.295728	2025-08-06 05:53:44.29573
28291372P	Dirterm flanged deaerator DN100 10 BAR	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	326	2025-08-06 05:53:44.296451	2025-08-06 05:53:44.296453
28291472P	Dirterm flanged deaerator DN125 10 BAR	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	327	2025-08-06 05:53:44.297141	2025-08-06 05:53:44.297143
28291572P	Dirterm flanged deaerator DN150 10 BAR	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	328	2025-08-06 05:53:44.297698	2025-08-06 05:53:44.2977
28310400	Airterm Dirt Self-cleaning Air & Dirt separator 1/2" (15mm)	\N	505.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	329	2025-08-06 05:53:44.29824	2025-08-06 05:53:44.298242
28310500	Airterm Dirt Self-cleaning Air & Dirt separator 3/4" (20mm)	\N	515.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	330	2025-08-06 05:53:44.298805	2025-08-06 05:53:44.298807
28310600	Airterm Dirt Self-cleaning Air & Dirt separator 1" (25mm)	\N	525.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	331	2025-08-06 05:53:44.299362	2025-08-06 05:53:44.299364
28310700	Airterm Dirt Self-cleaning Air & Dirt separator 1"1/4 (32mm)	\N	662.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	332	2025-08-06 05:53:44.299908	2025-08-06 05:53:44.299911
28310972P	Airterm Dirt Self-cleaning Air & Dirt separator DN50	\N	2699.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	333	2025-08-06 05:53:44.30055	2025-08-06 05:53:44.300553
28311072P	Airterm Dirt Self-cleaning Air & Dirt separator DN65	\N	3060.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	334	2025-08-06 05:53:44.301601	2025-08-06 05:53:44.301605
28311172P	Airterm Dirt Self-cleaning Air & Dirt separator DN80	\N	3720.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	335	2025-08-06 05:53:44.302603	2025-08-06 05:53:44.302606
28311372P	Airterm Dirt Self-cleaning Air & Dirt separator DN100	\N	4280.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	336	2025-08-06 05:53:44.303742	2025-08-06 05:53:44.303745
28311472P	Airterm Dirt Self-cleaning Air & Dirt separator DN125	\N	6220.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	337	2025-08-06 05:53:44.30463	2025-08-06 05:53:44.304632
28311572P	Airterm Dirt Self-cleaning Air & Dirt separator DN150	\N	7650.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	338	2025-08-06 05:53:44.305599	2025-08-06 05:53:44.305601
28311672P	Airterm Dirt Self-cleaning Air & Dirt separator DN200	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	339	2025-08-06 05:53:44.306672	2025-08-06 05:53:44.306675
28311772P	Airterm Dirt Self-cleaning Air & Dirt separator DN250	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	340	2025-08-06 05:53:44.307546	2025-08-06 05:53:44.307548
28311872P	Airterm Dirt Self-cleaning Air & Dirt separator DN300	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	341	2025-08-06 05:53:44.308177	2025-08-06 05:53:44.308179
6170612	1" (25mm) Threaded hydraulic separator	\N	1579.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	342	2025-08-06 05:53:44.308801	2025-08-06 05:53:44.308803
6170712	1-1/4" (32mm) Threaded hydraulic separator	\N	1820.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	343	2025-08-06 05:53:44.309443	2025-08-06 05:53:44.309445
6170812	1-1/2" (40mm) Threaded hydraulic separator	\N	2350.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	344	2025-08-06 05:53:44.310037	2025-08-06 05:53:44.310039
6170912	2" (50mm) Threaded hydraulic separator	\N	3535.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	345	2025-08-06 05:53:44.31066	2025-08-06 05:53:44.310661
6170972	Flanged Hydraulic Separator DN50	\N	5190.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	346	2025-08-06 05:53:44.311297	2025-08-06 05:53:44.3113
6171072	Flanged Hydraulic Separator DN65	\N	5485.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	347	2025-08-06 05:53:44.311891	2025-08-06 05:53:44.311893
6171172	Flanged Hydraulic Separator DN80	\N	8010.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	348	2025-08-06 05:53:44.312507	2025-08-06 05:53:44.31251
6171372	Flanged Hydraulic Separator DN100	\N	8780.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	349	2025-08-06 05:53:44.313315	2025-08-06 05:53:44.313318
6171472	Flanged Hydraulic Separator DN125	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	350	2025-08-06 05:53:44.314157	2025-08-06 05:53:44.314159
6171572	Flanged Hydraulic Separator DN150	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	351	2025-08-06 05:53:44.314993	2025-08-06 05:53:44.314995
37150510	MG2 Compact Magnetic Filter G3/4" (20mm)	\N	540.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	352	2025-08-06 05:53:44.315659	2025-08-06 05:53:44.315661
30700500	MG1 Compact Magnetic Filter G3/4" (20mm)	\N	384.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	353	2025-08-06 05:53:44.316306	2025-08-06 05:53:44.316309
36990600	MP1 Heat pump magnetic filter FF 1" (25mm)	\N	905.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	354	2025-08-06 05:53:44.317154	2025-08-06 05:53:44.317156
36990700	MP1 Heat pump magnetic filter FF 1-1/4" (32mm)	\N	0.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	355	2025-08-06 05:53:44.318105	2025-08-06 05:53:44.318107
38330600	MP2 Heat pump magnetic filter FF 1" (25mm)	\N	783.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	356	2025-08-06 05:53:44.318821	2025-08-06 05:53:44.318823
24050500	Safecleaner2 Magnetic Filter 3/4" (20mm)	\N	529.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	357	2025-08-06 05:53:44.319566	2025-08-06 05:53:44.319568
24050600	Safecleaner2 Magnetic Filter 1" (25mm)	\N	578.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	358	2025-08-06 05:53:44.320457	2025-08-06 05:53:44.32046
23440550	Safecleaner2 Magnetic Filter 3/4" (20mm) with FF Ball Valves	\N	690.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	359	2025-08-06 05:53:44.321497	2025-08-06 05:53:44.3215
23440650	Safecleaner2 Magnetic Filter 1" (25mm) with FF Ball Valves	\N	860.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	360	2025-08-06 05:53:44.322484	2025-08-06 05:53:44.322486
23440750	Safecleaner2 Magnetic Filter 1-1/4" (32mm) with FF Ball Valves	\N	910.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	361	2025-08-06 05:53:44.323266	2025-08-06 05:53:44.323268
23190550	Safecleaner 2, polymer diverter, FF ball valves G3/4" (20mm)	\N	550.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	362	2025-08-06 05:53:44.323908	2025-08-06 05:53:44.32391
23190650	Safecleaner 2, polymer diverter, FF ball valves G1" (25mm)	\N	710.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	363	2025-08-06 05:53:44.32448	2025-08-06 05:53:44.324482
23190750	Safecleaner 2, polymer diverter, FF ball valves G11/4 (32mm)	\N	755.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	364	2025-08-06 05:53:44.325103	2025-08-06 05:53:44.325105
35480500	Mag-nus2 Magnetic Dirt Separator G3/4" (20mm)	\N	763.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	365	2025-08-06 05:53:44.325685	2025-08-06 05:53:44.325687
28630500	Airterm Mag Air & Dirt Separator G3/4" (20mm)	\N	920.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	366	2025-08-06 05:53:44.326319	2025-08-06 05:53:44.32632
36020400	MG Magnetic Self-Cleaning Dirt Separator G1/2" (15mm)	\N	4559.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	367	2025-08-06 05:53:44.326926	2025-08-06 05:53:44.326928
36020500	MG Magnetic Self-Cleaning Dirt Separator G3/4" (20mm)	\N	4582.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	368	2025-08-06 05:53:44.327497	2025-08-06 05:53:44.327499
36020600	MG Magnetic Self-Cleaning Dirt Separator G1" (25mm)	\N	4979.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	369	2025-08-06 05:53:44.328084	2025-08-06 05:53:44.328086
36020700	MG Magnetic Self-Cleaning Dirt Separator G1 1/4" (32mm)	\N	5035.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	370	2025-08-06 05:53:44.328701	2025-08-06 05:53:44.328703
36020800	MG Magnetic Self-Cleaning Dirt Separator G1 1/2" (40mm)	\N	5772.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	371	2025-08-06 05:53:44.329283	2025-08-06 05:53:44.329285
36020900	MG Magnetic Self-Cleaning Dirt Separator G2" (50mm)	\N	5833.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	372	2025-08-06 05:53:44.329873	2025-08-06 05:53:44.329875
35410910	MG Plus Magnetic Self-Cleaning Dirt Separator DN50	\N	13902.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	373	2025-08-06 05:53:44.330467	2025-08-06 05:53:44.330469
35411010	MG Plus Magnetic Self-Cleaning Dirt Separator DN65	\N	15475.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	374	2025-08-06 05:53:44.331048	2025-08-06 05:53:44.331051
35411110	MG Plus Magnetic Self-Cleaning Dirt Separator DN80	\N	16692.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	375	2025-08-06 05:53:44.331666	2025-08-06 05:53:44.331667
35411310	MG Plus Magnetic Self-Cleaning Dirt Separator DN100	\N	18398.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	376	2025-08-06 05:53:44.332241	2025-08-06 05:53:44.332242
35411410	MG Plus Magnetic Self-Cleaning Dirt Separator DN125	\N	25259.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	377	2025-08-06 05:53:44.332823	2025-08-06 05:53:44.332825
35411510	MG Plus Magnetic Self-Cleaning Dirt Separator DN150	\N	28200.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	378	2025-08-06 05:53:44.333433	2025-08-06 05:53:44.333435
32860500	NT1 Acid Condensation Neutralising Filter	\N	277.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	379	2025-08-06 05:53:44.33403	2025-08-06 05:53:44.334032
32870516	Pair of Straight hose connection fittings 3/4" DN16	\N	57.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	380	2025-08-06 05:53:44.335305	2025-08-06 05:53:44.335312
32870520	Pair of Straight hose connection fittings 3/4" DN20	\N	59.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	381	2025-08-06 05:53:44.33637	2025-08-06 05:53:44.336375
32880516	Pair of Elbow hose connection fittings 3/4" DN16	\N	74.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	382	2025-08-06 05:53:44.337317	2025-08-06 05:53:44.33732
32880520	Pair of Elbow hose connection fittings 3/4" DN20	\N	76.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	383	2025-08-06 05:53:44.338026	2025-08-06 05:53:44.338028
32890000	Insulation shell for NT1	\N	190.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	384	2025-08-06 05:53:44.338675	2025-08-06 05:53:44.338676
32900000	Neutralising load of calcium carbonate (CaC03)	\N	125.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	385	2025-08-06 05:53:44.339313	2025-08-06 05:53:44.339315
39370000	TL1 by Piero Lissoni thermostatic radiator head	\N	69.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	386	2025-08-06 05:53:44.33991	2025-08-06 05:53:44.339912
41960000	Pair of temperature limiting inserts for TL1	\N	8.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	387	2025-08-06 05:53:44.340514	2025-08-06 05:53:44.340516
5900000	TL10 Thermostatic head with liquid expansion sensor	\N	50.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	388	2025-08-06 05:53:44.341132	2025-08-06 05:53:44.341143
7200030	TL30 Thermostatic head with liquid expansion sensor	\N	66.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	389	2025-08-06 05:53:44.34173	2025-08-06 05:53:44.341733
26330000	TL70 Thermostatic head with liquid expansion sensor	\N	63.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	390	2025-08-06 05:53:44.342336	2025-08-06 05:53:44.342338
30870000	TL10W Thermostatic head with liquid expansion sensor	\N	101.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	391	2025-08-06 05:53:44.342929	2025-08-06 05:53:44.342931
5900010	TL20 Thermostatic head with distance sensor	\N	220.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	392	2025-08-06 05:53:44.343513	2025-08-06 05:53:44.343515
480400	G1/2" Angle radiator valve with thermostatic option for copper or poly pipe	\N	57.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	393	2025-08-06 05:53:44.34409	2025-08-06 05:53:44.344092
490400	G1/2" Straight radiator valve with thermostatic option for copper or poly pipe	\N	70.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	394	2025-08-06 05:53:44.344699	2025-08-06 05:53:44.344701
290400	G1/2" Angle lockshield radiator valve copper or poly pipe	\N	55.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	395	2025-08-06 05:53:44.345293	2025-08-06 05:53:44.345295
300400	G1/2" Straight lockshield radiator valve copper or poly pipe	\N	65.00	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	396	2025-08-06 05:53:44.34588	2025-08-06 05:53:44.345883
711600	Compression fitting for polyethyle pipe to suit 16x2	\N	16.50	\N	\N	\N	\N	C1	\N	\N	\N	\N	\N	t	0	0	0	\N	397	2025-08-06 05:53:44.346457	2025-08-06 05:53:44.346459
\.


--
-- TOC entry 5247 (class 0 OID 16650)
-- Dependencies: 240
-- Data for Name: quote_line_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quote_line_items (option_id, product_id, quantity, unit_price, notes, discount, display_order, custom_sku, custom_name, custom_description, id, created_at, updated_at) FROM stdin;
1	2	92	96.00	Rinox Plus M G3/4" (20mm) Pressure reducing valve	70.00	1	\N	\N	\N	1	2025-08-06 06:04:57.698516	2025-08-06 06:05:31.108756
1	3	6	240.00	Rinox Plus M G1" (25mm) Pressure reducing valve	70.00	2	\N	\N	\N	2	2025-08-06 06:05:40.847489	2025-08-06 06:05:48.128702
1	4	35	340.00	Rinox Plus M G1 1/4" (32mm) Pressure reducing valve	70.00	3	\N	\N	\N	3	2025-08-06 06:06:24.773068	2025-08-06 06:06:28.705567
1	5	72	448.00	Rinox Plus M G1 1/2" (40mm) Pressure reducing valve	70.00	4	\N	\N	\N	4	2025-08-06 06:06:36.160803	2025-08-06 06:06:41.128403
\.


--
-- TOC entry 5249 (class 0 OID 16659)
-- Dependencies: 242
-- Data for Name: quote_options; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quote_options (quote_id, name, freight_charge, lead_time_value, lead_time_unit, is_ex_stock_brisbane, description, is_recommended, id, created_at, updated_at) FROM stdin;
1	Main Option	0.00	\N	\N	t	\N	f	1	2025-08-06 06:04:49.546857	2025-08-06 06:06:44.635423
\.


--
-- TOC entry 5251 (class 0 OID 16665)
-- Dependencies: 244
-- Data for Name: quote_recipients; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quote_recipients (deal_id, company_id, contact_person, delivery_method, special_instructions, id, created_at, updated_at) FROM stdin;
1	1	\N	email	\N	1	2025-08-06 06:04:45.006338	2025-08-06 06:04:45.006341
\.


--
-- TOC entry 5253 (class 0 OID 16671)
-- Dependencies: 246
-- Data for Name: quote_snapshots; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quote_snapshots (id, quote_option_id, version_number, created_at, updated_at, created_by_id, deleted_at, deleted_by_id, is_deleted, rendered_html, snapshot_metadata) FROM stdin;
1	1	1	2025-08-24 07:57:46.998558	2025-08-24 07:57:46.998571	2	\N	\N	f	<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <title>Quotation - Lorimer St</title>\n    <!-- Try external CSS first, fall back to inline -->\n    <link rel="stylesheet" href="/static/css/quote_pdf.css">\n    <style>\n        @page {\n    size: A4;\n    margin: 0.5cm 1.5cm 0.5cm 1.5cm; /* matched bottom margin to top margin */\n    @top-left {\n        content: element(header);\n    }\n}\nbody {\n    font-family: 'Helvetica', 'Arial', sans-serif;\n    font-size: 12px;\n    color: #333333;\n    background: #fff;\n    min-height: 100vh;\n    display: flex;\n    flex-direction: column;\n}\nheader {\n    position: running(header);\n    width: 100%;\n}\n\nfooter {\n    width: 100%;\n    text-align: center;\n    font-size: 9px;\n    color: #555555;\n    border-top: 1px solid #cccccc;\n    padding-top: 8px;\n    margin-top: 0;\n    page-break-inside: avoid;\n}\n\n/* Content wrapper for proper layout */\n.content-wrapper {\n    display: flex;\n    flex-direction: column;\n}\n\n/* Quote body styling */\n.quote-body {\n    max-width: 1050px;\n    margin: 0 auto;\n    width: 100%;\n}\n\n/* Footer styling for last page only */\n.header-table {\n    width: 100%;\n    border-collapse: collapse;\n    color: #fff;\n    border-radius: 6px 6px 0 0;\n}\n.header-table td {\n    border: none;\n    padding: 10px 0 10px 10px;\n    vertical-align: top;\n}\n.logo {\n    max-width: 180px;\n    max-height: 60px;\n    background: #fff;\n    border-radius: 4px;\n    padding: 4px;\n}\n.quote-title-container {\n    padding: 10px 10px 5px 10px;\n    color: #fff;\n    text-align: right;\n    font-size: 22px;\n    font-weight: bold;\n    border-radius: 4px;\n    margin-bottom: 8px;\n}\n.quote-title {\n    font-size: 22px;\n    font-weight: bold;\n    letter-spacing: 1px;\n}\n.info-table {\n    width: 100%;\n    border-collapse: separate;\n    border-spacing: 0 4px;\n    margin-bottom: 10px;\n}\n.info-table td {\n    border: none;\n    padding: 2px 0;\n    vertical-align: top;\n}\n.text-right { text-align: right; }\n\n.main-table {\n    width: 100%;\n    max-width: 1050px;\n    border-collapse: collapse;\n    margin-top: 18px;\n    margin-bottom: 10px;\n    background: #fff;\n    border-radius: 6px;\n    overflow: hidden;\n}\n.main-table th {\n    color: #fff;\n    border: none;\n    padding: 10px 8px;\n    font-size: 12px;\n    font-weight: bold;\n    text-align: left;\n    background: #982d31;\n}\n.main-table td {\n    border: none;\n    padding: 8px;\n    background: #fff;\n    font-size: 12px;\n    vertical-align: top;\n}\n.main-table td small {\n    font-size: 9px;\n    color: #666;\n}\n/* Zebra striping for main table - light grey alternating rows */\n.main-table tr:nth-child(even) td {\n    background: #f8f8f8 !important;\n}\n.main-table tr:hover td {\n    background: #f8f9fa;\n}\n.totals-table-container {\n    display: block;\n    width: 100%;\n    max-width: 1050px;\n    margin: 0 auto 24px auto;\n    text-align: right;\n}\n.totals-table {\n    width: 340px;\n    max-width: 340px;\n    margin: 0 0 0 auto;\n    border-radius: 8px;\n    box-shadow: 0 2px 8px rgba(0,0,0,0.04);\n    overflow: hidden;\n    border-collapse: collapse;\n    float: right;\n}\n\n/* Remove header row from totals table */\n.totals-table thead {\n    display: none;\n}\n\n.totals-table td {\n    border: none;\n    padding: 10px 18px;\n    font-size: 1em;\n    text-align: right;\n}\n.totals-table td:first-child {\n    text-align: left;\n}\n\n/* Blank row above subtotal with rounded corners and division color */\n.totals-table tbody tr:first-child td:first-child {\n    background: #982d31 !important;\n    color: #ffffff !important;\n    border-top-left-radius: 8px;\n    padding: 8px 18px;\n}\n.totals-table tbody tr:first-child td:last-child {\n    background: #982d31 !important;\n    color: #ffffff !important;\n    border-top-right-radius: 8px;\n    padding: 8px 18px;\n}\n\n/* Division-specific colors for the blank row - higher specificity */\n.totals-table.hvac-color tbody tr:first-child td:first-child,\n.totals-table.hvac-color tbody tr:first-child td:last-child {\n    background: #799285 !important;\n    color: #ffffff !important;\n}\n.totals-table.plumbing-color tbody tr:first-child td:first-child,\n.totals-table.plumbing-color tbody tr:first-child td:last-child {\n    background: #37779e !important;\n    color: #ffffff !important;\n}\n.totals-table.hydronic-color tbody tr:first-child td:first-child,\n.totals-table.hydronic-color tbody tr:first-child td:last-child {\n    background: #982d31 !important;\n    color: #ffffff !important;\n}\n\n/* Zebra striping for totals table - match PDF exactly */\n.totals-table tbody tr:nth-child(odd):not(:first-child) td {\n    background: #f8f8f8 !important;\n}\n.totals-table tbody tr:nth-child(even):not(:first-child) td {\n    background: #ffffff !important;\n}\n\n/* Freight row styling with black borders - match PDF exactly */\n.totals-table tbody tr:nth-child(3) td {\n    border-top: 1px solid #000000 !important;\n    border-bottom: 1px solid #000000 !important;\n    background: #ffffff !important;\n}\n\n/* Grand total styling - match PDF exactly */\n.totals-table tbody tr.grand-total td {\n    background: #982d31 !important;\n    color: #ffffff !important;\n    font-weight: bold;\n    font-size: 1.2em;\n}\n.totals-table tbody tr.grand-total td:first-child {\n    border-bottom-left-radius: 8px;\n}\n.totals-table tbody tr.grand-total td:last-child {\n    border-bottom-right-radius: 8px;\n}\n\n/* Ensure grand total has proper styling for all quote types - maximum specificity */\n.totals-table.hvac-color tbody tr.grand-total td { \n    background: #799285 !important; \n    color: #ffffff !important; \n    font-weight: bold;\n    font-size: 1.2em;\n}\n.totals-table.plumbing-color tbody tr.grand-total td { \n    background: #37779e !important; \n    color: #ffffff !important; \n    font-weight: bold;\n    font-size: 1.2em;\n}\n.totals-table.hydronic-color tbody tr.grand-total td { \n    background: #982d31 !important; \n    color: #ffffff !important; \n    font-weight: bold;\n    font-size: 1.2em;\n}\n\n.comments {\n    margin-bottom: 25px;\n    font-size: 11px;\n    background: #eaf1ed;\n    padding: 8px 12px;\n    border-left: 4px solid #799285;\n    border-radius: 4px;\n}\n.terms {\n    font-size: 9px;\n    color: #555555;\n    page-break-inside: avoid;\n    margin-bottom: 15px;\n}\n\n.footer-bottom {\n    margin-top: auto;\n    padding: 20px 0;\n    border-top: 1px solid #cccccc;\n    text-align: center;\n    page-break-inside: avoid;\n    background: white;\n    position: relative;\n    bottom: 0;\n}\n\n.company-info {\n    font-size: 9px;\n    color: #555555;\n    margin-top: 15px;\n    line-height: 1.4;\n}\n\n.business-details {\n    font-size: 9px;\n    color: #555555;\n    page-break-inside: avoid;\n    line-height: 1.4;\n    margin: 0;\n    padding: 0;\n}\n\n/* --- UPDATED RULES --- */\n.totals-terms-section {\n    page-break-inside: avoid;\n    margin-bottom: 20px;\n}\n\n.hvac-color th, .hvac-color .main-table td { background: #799285 !important; }\n.plumbing-color th, .plumbing-color .main-table td { background: #37779e !important; }\n.hydronic-color th, .hydronic-color .main-table td { background: #982d31 !important; }\n/* Additional deal type colors - using existing color schemes */\n.data-centres-color th, .data-centres-color .main-table td { background: #799285 !important; }\n.merchant-color th, .merchant-color .main-table td { background: #37779e !important; }\n.wholesaler-color th, .wholesaler-color .main-table td { background: #37779e !important; }\n.oem-color th, .oem-color .main-table td { background: #37779e !important; }\nstrong { font-weight: bold; }\n.section-title {\n    font-size: 16px;\n    font-weight: bold;\n    margin-top: 24px;\n    margin-bottom: 12px;\n    letter-spacing: 1px;\n    padding: 6px 12px;\n    border-left: 6px solid #799285;\n    background: #f4f7f5;\n    color: #333;\n    border-radius: 4px;\n}\n\n/* Main table header colors for each division */\n.hvac-color .main-table th {\n    background: #799285 !important;\n    border-color: #799285 !important;\n}\n.plumbing-color .main-table th {\n    background: #37779e !important;\n    border-color: #37779e !important;\n}\n.hydronic-color .main-table th {\n    background: #982d31 !important;\n    border-color: #982d31 !important;\n}\n/* Additional deal type header colors - using existing color schemes */\n.data-centres-color .main-table th {\n    background: #799285 !important;\n    border-color: #799285 !important;\n}\n.merchant-color .main-table th {\n    background: #37779e !important;\n    border-color: #37779e !important;\n}\n.wholesaler-color .main-table th {\n    background: #37779e !important;\n    border-color: #37779e !important;\n}\n.oem-color .main-table th {\n    background: #37779e !important;\n    border-color: #37779e !important;\n}\n        \n        body { margin-top: 0; }\n        .main-container {\n            max-width: 1050px;\n            margin: 0 auto;\n        }\n        .top-banner {\n            color: #fff;\n            padding: 0.5em 0.8em 0.5em 0.8em;\n            border-top-left-radius: 16px;\n            border-top-right-radius: 16px;\n            width: 100%;\n            box-sizing: border-box;\n        }\n        .banner-card {\n            background: #fff;\n            border-bottom-left-radius: 16px;\n            border-bottom-right-radius: 16px;\n            margin-bottom: 18px;\n            box-shadow: 0 2px 8px rgba(0,0,0,0.03);\n            padding: 0 0 0.5em 0;\n            width: 100%;\n            box-sizing: border-box;\n        }\n        .deal-title { font-size: 1.5em; font-weight: bold; letter-spacing: 1px; }\n        .subsection { background: #f8f8f8; padding: 10px 18px; border-radius: 0 0 6px 6px; margin-bottom: 18px; font-size: 1em; }\n        .totals-table {\n            border-collapse: separate;\n            border-spacing: 0;\n            border-bottom-left-radius: 16px;\n            border-bottom-right-radius: 16px;\n            overflow: hidden;\n            margin-bottom: 0;\n        }\n        .grand-total {\n            border-radius: 0 0 16px 16px !important;\n        }\n        /* Zebra striping for main table rows */\n        .main-table tr:nth-child(even) td {\n            background: #f8f8f8 !important;\n        }\n    </style>\n</head>\n<body>\n    \n    \n    <div class="top-banner plumbing-color" style="background: #37779e; width: 100%; max-width: 1050px; margin: 0 auto;">\n        <table class="header-table" style="margin-bottom: 0; width: 100%;">\n            <tr>\n                <td style="width: 160px; vertical-align: middle;">\n                    \n                    <!-- Use base64 embedded logo for PDF generation -->\n                    <img src="data:image/png;base64,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AAAAAAAAAAAAyig2AAAAAAAAAAAAAAAAZRQbAAAAAAAAAAAAAACAMooNAAAAAAAAAAAAAABAGcUGAAAAAAAAAAAAAACgjGIDAAAAAAAAAAAAAABQRrEBAAAAAAAAAAAAAAAoo9gAAAAAAAAAAAAAAACUUWwAAAAAAAAAAAAAAADKKDYAAAAAAAAAAAAAAABlFBsAAAAAAAAAAAAAAIAyig0AAAAAAAAAAAAAAEAZxQYAAAAAAAAAAAAAAKCMYgMAAAAAAAAAAAAAAFBGsQEAAAAAAAAAAAAAACij2AAAAAAAAAAAAAAAAJRRbAAAAAAAAAAAAAAAAMooNgAAAAAAAAAAAAAAAGUUGwAAAAAAAAAAAAAAgDKKDQAAAAAAAAAAAAAAQBnFBgAAAAAAAAAAAAAAoIxiAwAAAAAAAAAAAAAAUEaxAQAAAAAAAAAAAAAAKKPYAAAAAAAAAAAAAAAAlFFsAAAAAAAAAAAAAAAAyig2AAAAAAAAAAAAAAAAZRQbAAAAAAAAAAAAAACAMooNAAAAAAAAAAAAAABAGcUGAAAAAAAAAAAAAACgjGIDAAAAAAAAAAAAAABQRrEBAAAAAAAAAAAAAAAoo9gAAAAAAAAAAAAAAACUUWwAAAAAAAAAAAAAAADKKDYAAAAAAAAAAAAAAABlFBsAAAAAAAAAAAAAAIAyig0AAAAAAAAAAAAAAEAZxQYAAAAAAAAAAAAAAKCMYgMAAAAAAAAAAAAAAFBGsQEAAAAAAAAAAAAAACij2AAAAAAAAAAAAAAAAJRRbAAAAAAAAAAAAAAAAMooNgAAAAAAAAAAAAAAAGUUGwAAAAAAAAAAAAAAgDKKDQAAAAAAAAAAAAAAQBnFBgAAAAAAAAAAAAAAoIxiAwAAAAAAAAAAAAAAUEaxAQAAAAAAAAAAAAAAKKPYAAAAAAAAAAAAAAAAlFFsAAAAAAAAAAAAAAAAyig2AAAAAAAAAAAAAAAAZRQbAAAAAAAAAAAAAACAMooNAAAAAAAAAAAAAABAGcUGAAAAAAAAAAAAAACgjGIDAAAAAAAAAAAAAABQRrEBAAAAAAAAAAAAAAAoo9gAAAAAAAAAAAAAAACUUWwAAAAAAAAAAAAAAADKKDYAAAAAAAAAAAAAAABlFBsAAAAAAAAAAAAAAIAyig0AAAAAAAAAAAAAAEAZxQYAAAAAAAAAAAAA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" alt="RBM Systems Company Logo (full color)" class="logo">\n                    \n                    <!-- Debug info (will be hidden in PDF) -->\n                    \n                    <!-- Logo data URL available (data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAADDYA...) -->\n                    \n                </td>\n                <td style="vertical-align: middle; text-align: right;">\n                    <span class="deal-title" style="font-size: 28px; font-weight: bold; letter-spacing: 1px;">Lorimer St</span>\n                </td>\n            </tr>\n        </table>\n    </div>\n    <div class="banner-card" style="width: 100%; max-width: 1050px; margin: 0 auto;">\n        <div class="subsection">\n            <table style="width: 100%; border: none;">\n                <tr>\n                    <td style="width: 60%; vertical-align: top;">\n                        <strong>To:</strong> <strong>Drillcut</strong><br>\n                        \n                            <strong>Attn:</strong> Gary Shirreff<br>\n                            \n                                <strong>Phone:</strong> +61437009205<br>\n                            \n                            \n                                <strong>Email:</strong> Gary.Shirreff@drillcut.com.au<br>\n                            \n                        \n                    </td>\n                    <td style="width: 40%; vertical-align: top; text-align: right;">\n                        <strong>Quote Reference:</strong> 1-1<br>\n                        <strong>Option:</strong> Main Option<br>\n                        <strong>Date:</strong> 24-08-2025<br>\n                        <strong>Valid Until:</strong> 24-09-2025<br>\n                        <br>\n                        <strong>Created By:</strong> Owen Dayton<br>\n                        owen@rbmsystems.com.au\n                    </td>\n                </tr>\n            </table>\n        </div>\n    </div>\n    \n    <div class="content-wrapper">\n\n    \n\n    \n    <section class="lead-time" style="background: #f8f9fa; border-left: 4px solid #37779e; border-top-left-radius: 8px; border-bottom-left-radius: 8px; max-width: 1050px; margin: 0 0 20px 0; padding: 12px 20px;">\n        Current lead-time is Ex-Stock Brisbane from receipt of order subject to prior order and logistics.\n    </section>\n    \n\n    <section class="quote-body" style="max-width: 1050px; margin: 0 auto;">\n        \n            \n            <table class="main-table" style="width: 100%;">\n                <thead>\n                    <tr class="plumbing-color">\n                        <th style="width: 45%;">Description</th>\n                        <th style="width: auto; white-space: nowrap;" class="text-right">Qty</th>\n                        <th style="width: auto; white-space: nowrap;" class="text-right">List Price</th>\n                        <th style="width: auto; white-space: nowrap;" class="text-right">Discount</th>\n                        <th style="width: auto; white-space: nowrap;" class="text-right">Nett Price</th>\n                        <th style="width: auto; white-space: nowrap;" class="text-right">Total Price</th>\n                    </tr>\n                </thead>\n                <tbody>\n                    \n                    <tr>\n                        <td>\n                            <strong>Rinox Plus M G3/4&#34; (20mm) Pressure reducing valve</strong>\n                            <br><small>SKU: 25810500</small>\n                            \n                            \n                        </td>\n                        <td class="text-right">92</td>\n                        <td class="text-right">$96.00</td>\n                        <td class="text-right">70.00%</td>\n                        <td class="text-right">$28.80</td>\n                        <td class="text-right">$2,649.60</td>\n                    </tr>\n                    \n                    <tr>\n                        <td>\n                            <strong>Rinox Plus M G1&#34; (25mm) Pressure reducing valve</strong>\n                            <br><small>SKU: 25810600</small>\n                            \n                            \n                        </td>\n                        <td class="text-right">6</td>\n                        <td class="text-right">$240.00</td>\n                        <td class="text-right">70.00%</td>\n                        <td class="text-right">$72.00</td>\n                        <td class="text-right">$432.00</td>\n                    </tr>\n                    \n                    <tr>\n                        <td>\n                            <strong>Rinox Plus M G1 1/4&#34; (32mm) Pressure reducing valve</strong>\n                            <br><small>SKU: 25810700</small>\n                            \n                            \n                        </td>\n                        <td class="text-right">35</td>\n                        <td class="text-right">$340.00</td>\n                        <td class="text-right">70.00%</td>\n                        <td class="text-right">$102.00</td>\n                        <td class="text-right">$3,570.00</td>\n                    </tr>\n                    \n                    <tr>\n                        <td>\n                            <strong>Rinox Plus M G1 1/2&#34; (40mm) Pressure reducing valve</strong>\n                            <br><small>SKU: 25810800</small>\n                            \n                            \n                        </td>\n                        <td class="text-right">72</td>\n                        <td class="text-right">$448.00</td>\n                        <td class="text-right">70.00%</td>\n                        <td class="text-right">$134.40</td>\n                        <td class="text-right">$9,676.80</td>\n                    </tr>\n                    \n                </tbody>\n            </table>\n            \n        \n        <div class="totals-table-container">\n            <table class="totals-table plumbing-color">\n                <tbody>\n                    <tr>\n                        <td></td>\n                        <td></td>\n                    </tr>\n                    <tr>\n                        <td><strong>Subtotal</strong></td>\n                        <td class="text-right">$16,328.40</td>\n                    </tr>\n                    <tr>\n                        <td><strong>Freight</strong></td>\n                        <td class="text-right">$0.00</td>\n                    </tr>\n                    <tr class="grand-total">\n                        <td><strong>Total (Excluding GST)</strong></td>\n                        <td class="text-right">$16,328.40</td>\n                    </tr>\n                </tbody>\n            </table>\n        </div>\n    </section>\n\n    <section class="totals-terms-section">\n        \n    </section>\n    </div>\n    \n    <!-- Footer with Terms & Conditions and Company Info - appears at very bottom of last page -->\n    <div class="footer-bottom">\n        <div class="terms">\n            <strong>Terms & Conditions</strong><br>\n            All pricing quoted in AUD$ and is exclusive of GST.<br>\n            RBM General Conditions of Sale - Australia apply, for a copy please visit our website.\n        </div>\n        <div class="company-info" style="font-size: 13px;">\n            <strong>RBM Systems PTY LTD</strong><br>\n            ABN: 86 640 763 239 | PO Box 4104, Gumdale, QLD, 4154<br>\n            P: <strong>+61 7 3073 2428</strong> | E: <a href="mailto:hello@rbmsystems.com.au" style="color: #0066cc; text-decoration: underline;">hello@rbmsystems.com.au</a> | W: <a href="https://www.rbmsystems.com.au" style="color: #0066cc; text-decoration: underline;">https://www.rbmsystems.com.au</a>\n        </div>\n    </div>\n    \n</body>\n</html>	{"total_amount": 16328.4, "line_item_count": 4, "quote_option_name": "Main Option", "deal_type": "Plumbing", "customer_name": "Drillcut", "freight_charge": 0.0, "created_at_iso": "2025-08-24T07:57:46.996014+00:00", "pdf_generated": true, "template_used": "deals/pdf/plumbing_quote_template.html"}
\.


--
-- TOC entry 5255 (class 0 OID 16681)
-- Dependencies: 248
-- Data for Name: quotes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotes (recipient_id, revision, notes, created_at, valid_until, status, total_discount, id, updated_at) FROM stdin;
1	1	New blank quote.	2025-08-06 06:04:49.543829	\N	draft	0.00	1	2025-08-06 06:04:49.543833
\.


--
-- TOC entry 5257 (class 0 OID 16687)
-- Dependencies: 250
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (title, description, task_type, priority, status, due_date, start_date, completed_date, estimated_hours, actual_hours, assigned_to_id, created_by_id, company_id, contact_id, deal_id, is_recurring, recurrence_pattern, recurrence_interval, parent_task_id, tags, notes, completion_notes, id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5259 (class 0 OID 16693)
-- Dependencies: 252
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (username, email, password_hash, first_name, last_name, phone_number, role, is_active, last_login, force_password_change, id, created_at, updated_at, two_factor_enabled, two_factor_secret, backup_codes) FROM stdin;
admin	admin@rbm.com	scrypt:32768:8:1$uB1FrFzPUQZa8hBZ$1b1f4322e80c7c8d4c06bd39469c7a7f3231bf09e216231c3f038d76ff59c03c830cdbc2322b41b783980ad1b637ff14f6016126dd0eab7dd6e6932bead4ae23	Admin	User	\N	ADMIN	t	2025-08-06 06:01:44.14935	f	1	2025-08-06 05:59:25.233311	2025-08-06 06:01:44.150404	f	\N	\N
owen.dayton	owen@rbmsystems.com.au	scrypt:32768:8:1$YZGttj0OTxAHlwMy$b5d5129bfafd394580ab54b01c46d90a9c2027605f1206e5e9db55670c2e0b81172b0a3607fd8d0cb45adc9005c27d2ddbb1f402e589d75708351fae4b110346	Owen	Dayton	+61490537055	SALES	t	2025-09-05 05:24:21.369071	f	2	2025-08-06 06:01:06.38934	2025-09-05 05:24:21.370597	f	\N	\N
\.


--
-- TOC entry 5284 (class 0 OID 0)
-- Dependencies: 218
-- Name: activities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.activities_id_seq', 1, false);


--
-- TOC entry 5285 (class 0 OID 0)
-- Dependencies: 221
-- Name: calls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.calls_id_seq', 1, false);


--
-- TOC entry 5286 (class 0 OID 0)
-- Dependencies: 223
-- Name: companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.companies_id_seq', 1, false);


--
-- TOC entry 5287 (class 0 OID 0)
-- Dependencies: 225
-- Name: contacts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.contacts_id_seq', 1, false);


--
-- TOC entry 5288 (class 0 OID 0)
-- Dependencies: 229
-- Name: deals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.deals_id_seq', 1, false);


--
-- TOC entry 5289 (class 0 OID 0)
-- Dependencies: 231
-- Name: discounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.discounts_id_seq', 1, false);


--
-- TOC entry 5290 (class 0 OID 0)
-- Dependencies: 233
-- Name: emails_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.emails_id_seq', 1, false);


--
-- TOC entry 5291 (class 0 OID 0)
-- Dependencies: 235
-- Name: meetings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.meetings_id_seq', 1, false);


--
-- TOC entry 5292 (class 0 OID 0)
-- Dependencies: 237
-- Name: notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notes_id_seq', 1, false);


--
-- TOC entry 5293 (class 0 OID 0)
-- Dependencies: 239
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 1, false);


--
-- TOC entry 5294 (class 0 OID 0)
-- Dependencies: 241
-- Name: quote_line_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quote_line_items_id_seq', 1, false);


--
-- TOC entry 5295 (class 0 OID 0)
-- Dependencies: 243
-- Name: quote_options_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quote_options_id_seq', 1, false);


--
-- TOC entry 5296 (class 0 OID 0)
-- Dependencies: 245
-- Name: quote_recipients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quote_recipients_id_seq', 1, false);


--
-- TOC entry 5297 (class 0 OID 0)
-- Dependencies: 247
-- Name: quote_snapshots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quote_snapshots_id_seq', 1, false);


--
-- TOC entry 5298 (class 0 OID 0)
-- Dependencies: 249
-- Name: quotes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quotes_id_seq', 1, false);


--
-- TOC entry 5299 (class 0 OID 0)
-- Dependencies: 251
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_id_seq', 1, false);


--
-- TOC entry 5300 (class 0 OID 0)
-- Dependencies: 253
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- TOC entry 4910 (class 2606 OID 16718)
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (id);


--
-- TOC entry 4926 (class 2606 OID 16720)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 4928 (class 2606 OID 16722)
-- Name: calls calls_activity_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calls
    ADD CONSTRAINT calls_activity_id_key UNIQUE (activity_id);


--
-- TOC entry 4930 (class 2606 OID 16724)
-- Name: calls calls_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calls
    ADD CONSTRAINT calls_pkey PRIMARY KEY (id);


--
-- TOC entry 4937 (class 2606 OID 16726)
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- TOC entry 4942 (class 2606 OID 16728)
-- Name: contacts contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_pkey PRIMARY KEY (id);


--
-- TOC entry 4950 (class 2606 OID 16730)
-- Name: deal_companies deal_companies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deal_companies
    ADD CONSTRAINT deal_companies_pkey PRIMARY KEY (deal_id, company_id);


--
-- TOC entry 4952 (class 2606 OID 16732)
-- Name: deal_contacts deal_contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deal_contacts
    ADD CONSTRAINT deal_contacts_pkey PRIMARY KEY (deal_id, contact_id);


--
-- TOC entry 4954 (class 2606 OID 16734)
-- Name: deals deals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deals
    ADD CONSTRAINT deals_pkey PRIMARY KEY (id);


--
-- TOC entry 4964 (class 2606 OID 16736)
-- Name: discounts discounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.discounts
    ADD CONSTRAINT discounts_pkey PRIMARY KEY (id);


--
-- TOC entry 4968 (class 2606 OID 16738)
-- Name: emails emails_activity_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emails
    ADD CONSTRAINT emails_activity_id_key UNIQUE (activity_id);


--
-- TOC entry 4970 (class 2606 OID 16740)
-- Name: emails emails_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emails
    ADD CONSTRAINT emails_pkey PRIMARY KEY (id);


--
-- TOC entry 4985 (class 2606 OID 16742)
-- Name: meetings meetings_activity_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.meetings
    ADD CONSTRAINT meetings_activity_id_key UNIQUE (activity_id);


--
-- TOC entry 4987 (class 2606 OID 16744)
-- Name: meetings meetings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.meetings
    ADD CONSTRAINT meetings_pkey PRIMARY KEY (id);


--
-- TOC entry 4993 (class 2606 OID 16746)
-- Name: notes notes_activity_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_activity_id_key UNIQUE (activity_id);


--
-- TOC entry 4995 (class 2606 OID 16748)
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (id);


--
-- TOC entry 5005 (class 2606 OID 16750)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 5009 (class 2606 OID 16752)
-- Name: quote_line_items quote_line_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_line_items
    ADD CONSTRAINT quote_line_items_pkey PRIMARY KEY (id);


--
-- TOC entry 5013 (class 2606 OID 16754)
-- Name: quote_options quote_options_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_options
    ADD CONSTRAINT quote_options_pkey PRIMARY KEY (id);


--
-- TOC entry 5018 (class 2606 OID 16756)
-- Name: quote_recipients quote_recipients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_recipients
    ADD CONSTRAINT quote_recipients_pkey PRIMARY KEY (id);


--
-- TOC entry 5020 (class 2606 OID 16758)
-- Name: quote_snapshots quote_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_snapshots
    ADD CONSTRAINT quote_snapshots_pkey PRIMARY KEY (id);


--
-- TOC entry 5026 (class 2606 OID 16760)
-- Name: quotes quotes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quotes
    ADD CONSTRAINT quotes_pkey PRIMARY KEY (id);


--
-- TOC entry 5045 (class 2606 OID 16762)
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- TOC entry 5047 (class 2606 OID 16764)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 5049 (class 2606 OID 16766)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 5051 (class 2606 OID 16768)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 4911 (class 1259 OID 16769)
-- Name: idx_activity_company_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activity_company_date ON public.activities USING btree (company_id, created_at);


--
-- TOC entry 4912 (class 1259 OID 16770)
-- Name: idx_activity_contact_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activity_contact_date ON public.activities USING btree (contact_id, created_at);


--
-- TOC entry 4913 (class 1259 OID 16771)
-- Name: idx_activity_deal_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activity_deal_date ON public.activities USING btree (deal_id, created_at);


--
-- TOC entry 4914 (class 1259 OID 16772)
-- Name: idx_activity_scheduled; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activity_scheduled ON public.activities USING btree (scheduled_date);


--
-- TOC entry 4915 (class 1259 OID 16773)
-- Name: idx_activity_type_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activity_type_status ON public.activities USING btree (activity_type, status);


--
-- TOC entry 4916 (class 1259 OID 16774)
-- Name: idx_activity_user_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activity_user_date ON public.activities USING btree (user_id, created_at);


--
-- TOC entry 4931 (class 1259 OID 16775)
-- Name: idx_call_follow_up; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_call_follow_up ON public.calls USING btree (follow_up_required, follow_up_date);


--
-- TOC entry 4932 (class 1259 OID 16776)
-- Name: idx_call_outcome; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_call_outcome ON public.calls USING btree (outcome);


--
-- TOC entry 4933 (class 1259 OID 16777)
-- Name: idx_call_phone_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_call_phone_date ON public.calls USING btree (phone_number, created_at);


--
-- TOC entry 4938 (class 1259 OID 16778)
-- Name: idx_company_domain; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_company_domain ON public.companies USING btree (domain);


--
-- TOC entry 4943 (class 1259 OID 16779)
-- Name: idx_contact_company_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contact_company_active ON public.contacts USING btree (company_id, is_active);


--
-- TOC entry 4944 (class 1259 OID 16780)
-- Name: idx_contact_name_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contact_name_email ON public.contacts USING btree (name, email);


--
-- TOC entry 4945 (class 1259 OID 16781)
-- Name: idx_contact_primary; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contact_primary ON public.contacts USING btree (company_id, is_primary);


--
-- TOC entry 4955 (class 1259 OID 16782)
-- Name: idx_deal_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deal_active ON public.deals USING btree (is_active);


--
-- TOC entry 4956 (class 1259 OID 16783)
-- Name: idx_deal_close_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deal_close_date ON public.deals USING btree (expected_close_date);


--
-- TOC entry 4957 (class 1259 OID 16784)
-- Name: idx_deal_owner_stage; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deal_owner_stage ON public.deals USING btree (owner_id, stage);


--
-- TOC entry 4958 (class 1259 OID 16785)
-- Name: idx_deal_type_stage; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deal_type_stage ON public.deals USING btree (deal_type, stage);


--
-- TOC entry 4965 (class 1259 OID 16786)
-- Name: idx_discount_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_discount_active ON public.discounts USING btree (is_active);


--
-- TOC entry 4971 (class 1259 OID 16787)
-- Name: idx_email_recipient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_recipient ON public.emails USING btree (recipient_email);


--
-- TOC entry 4972 (class 1259 OID 16788)
-- Name: idx_email_sender; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_sender ON public.emails USING btree (sender_email);


--
-- TOC entry 4973 (class 1259 OID 16789)
-- Name: idx_email_subject; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_subject ON public.emails USING btree (subject);


--
-- TOC entry 4974 (class 1259 OID 16790)
-- Name: idx_email_thread; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_thread ON public.emails USING btree (email_thread_id);


--
-- TOC entry 4975 (class 1259 OID 16791)
-- Name: idx_email_unread; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_unread ON public.emails USING btree (is_read);


--
-- TOC entry 5006 (class 1259 OID 16792)
-- Name: idx_line_item_option_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_line_item_option_order ON public.quote_line_items USING btree (option_id, display_order);


--
-- TOC entry 4980 (class 1259 OID 16793)
-- Name: idx_meeting_follow_up; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_meeting_follow_up ON public.meetings USING btree (follow_up_required, follow_up_date);


--
-- TOC entry 4981 (class 1259 OID 16794)
-- Name: idx_meeting_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_meeting_location ON public.meetings USING btree (location);


--
-- TOC entry 4982 (class 1259 OID 16795)
-- Name: idx_meeting_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_meeting_type ON public.meetings USING btree (meeting_type);


--
-- TOC entry 4988 (class 1259 OID 16796)
-- Name: idx_note_important; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_note_important ON public.notes USING btree (is_important);


--
-- TOC entry 4989 (class 1259 OID 16797)
-- Name: idx_note_internal; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_note_internal ON public.notes USING btree (is_internal);


--
-- TOC entry 4990 (class 1259 OID 16798)
-- Name: idx_note_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_note_type ON public.notes USING btree (note_type);


--
-- TOC entry 4996 (class 1259 OID 16799)
-- Name: idx_product_category_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_product_category_active ON public.products USING btree (category, is_active);


--
-- TOC entry 4997 (class 1259 OID 16800)
-- Name: idx_product_item_no; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_product_item_no ON public.products USING btree (item_no);


--
-- TOC entry 4998 (class 1259 OID 16801)
-- Name: idx_product_series; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_product_series ON public.products USING btree (series);


--
-- TOC entry 4999 (class 1259 OID 16802)
-- Name: idx_product_sku_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_product_sku_name ON public.products USING btree (sku, name);


--
-- TOC entry 5010 (class 1259 OID 16803)
-- Name: idx_quote_option_quote; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_quote_option_quote ON public.quote_options USING btree (quote_id);


--
-- TOC entry 5014 (class 1259 OID 16804)
-- Name: idx_quote_recipient_deal_company; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_quote_recipient_deal_company ON public.quote_recipients USING btree (deal_id, company_id);


--
-- TOC entry 5021 (class 1259 OID 16805)
-- Name: idx_quote_recipient_revision; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_quote_recipient_revision ON public.quotes USING btree (recipient_id, revision);


--
-- TOC entry 5022 (class 1259 OID 16806)
-- Name: idx_quote_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_quote_status ON public.quotes USING btree (status);


--
-- TOC entry 5027 (class 1259 OID 16807)
-- Name: idx_task_assigned_due; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_assigned_due ON public.tasks USING btree (assigned_to_id, due_date);


--
-- TOC entry 5028 (class 1259 OID 16808)
-- Name: idx_task_company_due; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_company_due ON public.tasks USING btree (company_id, due_date);


--
-- TOC entry 5029 (class 1259 OID 16809)
-- Name: idx_task_contact_due; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_contact_due ON public.tasks USING btree (contact_id, due_date);


--
-- TOC entry 5030 (class 1259 OID 16810)
-- Name: idx_task_deal_due; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_deal_due ON public.tasks USING btree (deal_id, due_date);


--
-- TOC entry 5031 (class 1259 OID 16811)
-- Name: idx_task_overdue; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_overdue ON public.tasks USING btree (due_date, status);


--
-- TOC entry 5032 (class 1259 OID 16812)
-- Name: idx_task_status_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_status_priority ON public.tasks USING btree (status, priority);


--
-- TOC entry 4917 (class 1259 OID 16813)
-- Name: ix_activities_activity_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activities_activity_type ON public.activities USING btree (activity_type);


--
-- TOC entry 4918 (class 1259 OID 16814)
-- Name: ix_activities_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activities_company_id ON public.activities USING btree (company_id);


--
-- TOC entry 4919 (class 1259 OID 16815)
-- Name: ix_activities_contact_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activities_contact_id ON public.activities USING btree (contact_id);


--
-- TOC entry 4920 (class 1259 OID 16816)
-- Name: ix_activities_deal_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activities_deal_id ON public.activities USING btree (deal_id);


--
-- TOC entry 4921 (class 1259 OID 16817)
-- Name: ix_activities_scheduled_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activities_scheduled_date ON public.activities USING btree (scheduled_date);


--
-- TOC entry 4922 (class 1259 OID 16818)
-- Name: ix_activities_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activities_status ON public.activities USING btree (status);


--
-- TOC entry 4923 (class 1259 OID 16819)
-- Name: ix_activities_title; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activities_title ON public.activities USING btree (title);


--
-- TOC entry 4924 (class 1259 OID 16820)
-- Name: ix_activities_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activities_user_id ON public.activities USING btree (user_id);


--
-- TOC entry 4934 (class 1259 OID 16821)
-- Name: ix_calls_direction; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_calls_direction ON public.calls USING btree (direction);


--
-- TOC entry 4935 (class 1259 OID 16822)
-- Name: ix_calls_outcome; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_calls_outcome ON public.calls USING btree (outcome);


--
-- TOC entry 4939 (class 1259 OID 16823)
-- Name: ix_companies_company_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_companies_company_name ON public.companies USING btree (company_name);


--
-- TOC entry 4940 (class 1259 OID 16824)
-- Name: ix_companies_domain; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_companies_domain ON public.companies USING btree (domain);


--
-- TOC entry 4946 (class 1259 OID 16825)
-- Name: ix_contacts_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_contacts_company_id ON public.contacts USING btree (company_id);


--
-- TOC entry 4947 (class 1259 OID 16826)
-- Name: ix_contacts_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_contacts_email ON public.contacts USING btree (email);


--
-- TOC entry 4948 (class 1259 OID 16827)
-- Name: ix_contacts_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_contacts_name ON public.contacts USING btree (name);


--
-- TOC entry 4959 (class 1259 OID 16828)
-- Name: ix_deals_deal_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deals_deal_type ON public.deals USING btree (deal_type);


--
-- TOC entry 4960 (class 1259 OID 16829)
-- Name: ix_deals_owner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deals_owner_id ON public.deals USING btree (owner_id);


--
-- TOC entry 4961 (class 1259 OID 16830)
-- Name: ix_deals_project_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_deals_project_name ON public.deals USING btree (project_name);


--
-- TOC entry 4962 (class 1259 OID 16831)
-- Name: ix_deals_stage; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deals_stage ON public.deals USING btree (stage);


--
-- TOC entry 4966 (class 1259 OID 16832)
-- Name: ix_discounts_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_discounts_code ON public.discounts USING btree (code);


--
-- TOC entry 4976 (class 1259 OID 16833)
-- Name: ix_emails_direction; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_emails_direction ON public.emails USING btree (direction);


--
-- TOC entry 4977 (class 1259 OID 16834)
-- Name: ix_emails_recipient_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_emails_recipient_email ON public.emails USING btree (recipient_email);


--
-- TOC entry 4978 (class 1259 OID 16835)
-- Name: ix_emails_sender_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_emails_sender_email ON public.emails USING btree (sender_email);


--
-- TOC entry 4979 (class 1259 OID 16836)
-- Name: ix_emails_subject; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_emails_subject ON public.emails USING btree (subject);


--
-- TOC entry 4983 (class 1259 OID 16837)
-- Name: ix_meetings_meeting_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_meetings_meeting_type ON public.meetings USING btree (meeting_type);


--
-- TOC entry 4991 (class 1259 OID 16838)
-- Name: ix_notes_note_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notes_note_type ON public.notes USING btree (note_type);


--
-- TOC entry 5000 (class 1259 OID 16839)
-- Name: ix_products_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_category ON public.products USING btree (category);


--
-- TOC entry 5001 (class 1259 OID 16840)
-- Name: ix_products_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_is_active ON public.products USING btree (is_active);


--
-- TOC entry 5002 (class 1259 OID 16841)
-- Name: ix_products_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_name ON public.products USING btree (name);


--
-- TOC entry 5003 (class 1259 OID 16842)
-- Name: ix_products_sku; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_products_sku ON public.products USING btree (sku);


--
-- TOC entry 5007 (class 1259 OID 16843)
-- Name: ix_quote_line_items_option_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_line_items_option_id ON public.quote_line_items USING btree (option_id);


--
-- TOC entry 5011 (class 1259 OID 16844)
-- Name: ix_quote_options_quote_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_options_quote_id ON public.quote_options USING btree (quote_id);


--
-- TOC entry 5015 (class 1259 OID 16845)
-- Name: ix_quote_recipients_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_recipients_company_id ON public.quote_recipients USING btree (company_id);


--
-- TOC entry 5016 (class 1259 OID 16846)
-- Name: ix_quote_recipients_deal_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_recipients_deal_id ON public.quote_recipients USING btree (deal_id);


--
-- TOC entry 5023 (class 1259 OID 16847)
-- Name: ix_quotes_recipient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quotes_recipient_id ON public.quotes USING btree (recipient_id);


--
-- TOC entry 5024 (class 1259 OID 16848)
-- Name: ix_quotes_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quotes_status ON public.quotes USING btree (status);


--
-- TOC entry 5033 (class 1259 OID 16849)
-- Name: ix_tasks_assigned_to_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_assigned_to_id ON public.tasks USING btree (assigned_to_id);


--
-- TOC entry 5034 (class 1259 OID 16850)
-- Name: ix_tasks_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_company_id ON public.tasks USING btree (company_id);


--
-- TOC entry 5035 (class 1259 OID 16851)
-- Name: ix_tasks_contact_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_contact_id ON public.tasks USING btree (contact_id);


--
-- TOC entry 5036 (class 1259 OID 16852)
-- Name: ix_tasks_created_by_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_created_by_id ON public.tasks USING btree (created_by_id);


--
-- TOC entry 5037 (class 1259 OID 16853)
-- Name: ix_tasks_deal_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_deal_id ON public.tasks USING btree (deal_id);


--
-- TOC entry 5038 (class 1259 OID 16854)
-- Name: ix_tasks_due_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_due_date ON public.tasks USING btree (due_date);


--
-- TOC entry 5039 (class 1259 OID 16855)
-- Name: ix_tasks_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_priority ON public.tasks USING btree (priority);


--
-- TOC entry 5040 (class 1259 OID 16856)
-- Name: ix_tasks_start_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_start_date ON public.tasks USING btree (start_date);


--
-- TOC entry 5041 (class 1259 OID 16857)
-- Name: ix_tasks_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_status ON public.tasks USING btree (status);


--
-- TOC entry 5042 (class 1259 OID 16858)
-- Name: ix_tasks_task_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_task_type ON public.tasks USING btree (task_type);


--
-- TOC entry 5043 (class 1259 OID 16859)
-- Name: ix_tasks_title; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_title ON public.tasks USING btree (title);


--
-- TOC entry 5052 (class 2606 OID 16860)
-- Name: activities activities_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 5053 (class 2606 OID 16865)
-- Name: activities activities_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contacts(id);


--
-- TOC entry 5054 (class 2606 OID 16870)
-- Name: activities activities_deal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES public.deals(id);


--
-- TOC entry 5055 (class 2606 OID 16875)
-- Name: activities activities_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 5056 (class 2606 OID 16880)
-- Name: calls calls_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calls
    ADD CONSTRAINT calls_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- TOC entry 5057 (class 2606 OID 16885)
-- Name: contacts contacts_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 5058 (class 2606 OID 16890)
-- Name: deal_companies deal_companies_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deal_companies
    ADD CONSTRAINT deal_companies_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 5059 (class 2606 OID 16895)
-- Name: deal_companies deal_companies_deal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deal_companies
    ADD CONSTRAINT deal_companies_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES public.deals(id);


--
-- TOC entry 5060 (class 2606 OID 16900)
-- Name: deal_contacts deal_contacts_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deal_contacts
    ADD CONSTRAINT deal_contacts_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contacts(id);


--
-- TOC entry 5061 (class 2606 OID 16905)
-- Name: deal_contacts deal_contacts_deal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deal_contacts
    ADD CONSTRAINT deal_contacts_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES public.deals(id);


--
-- TOC entry 5062 (class 2606 OID 16910)
-- Name: deals deals_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deals
    ADD CONSTRAINT deals_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- TOC entry 5063 (class 2606 OID 16915)
-- Name: emails emails_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emails
    ADD CONSTRAINT emails_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- TOC entry 5064 (class 2606 OID 16920)
-- Name: meetings meetings_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.meetings
    ADD CONSTRAINT meetings_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- TOC entry 5065 (class 2606 OID 16925)
-- Name: notes notes_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- TOC entry 5066 (class 2606 OID 16930)
-- Name: products products_discount_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_discount_code_fkey FOREIGN KEY (discount_code) REFERENCES public.discounts(code);


--
-- TOC entry 5067 (class 2606 OID 16935)
-- Name: quote_line_items quote_line_items_option_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_line_items
    ADD CONSTRAINT quote_line_items_option_id_fkey FOREIGN KEY (option_id) REFERENCES public.quote_options(id);


--
-- TOC entry 5068 (class 2606 OID 16940)
-- Name: quote_line_items quote_line_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_line_items
    ADD CONSTRAINT quote_line_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- TOC entry 5069 (class 2606 OID 16945)
-- Name: quote_options quote_options_quote_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_options
    ADD CONSTRAINT quote_options_quote_id_fkey FOREIGN KEY (quote_id) REFERENCES public.quotes(id);


--
-- TOC entry 5070 (class 2606 OID 16950)
-- Name: quote_recipients quote_recipients_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_recipients
    ADD CONSTRAINT quote_recipients_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 5071 (class 2606 OID 16955)
-- Name: quote_recipients quote_recipients_deal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_recipients
    ADD CONSTRAINT quote_recipients_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES public.deals(id);


--
-- TOC entry 5072 (class 2606 OID 16960)
-- Name: quotes quotes_recipient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quotes
    ADD CONSTRAINT quotes_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES public.quote_recipients(id);


--
-- TOC entry 5073 (class 2606 OID 16965)
-- Name: tasks tasks_assigned_to_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_assigned_to_id_fkey FOREIGN KEY (assigned_to_id) REFERENCES public.users(id);


--
-- TOC entry 5074 (class 2606 OID 16970)
-- Name: tasks tasks_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 5075 (class 2606 OID 16975)
-- Name: tasks tasks_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contacts(id);


--
-- TOC entry 5076 (class 2606 OID 16980)
-- Name: tasks tasks_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- TOC entry 5077 (class 2606 OID 16985)
-- Name: tasks tasks_deal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES public.deals(id);


--
-- TOC entry 5078 (class 2606 OID 16990)
-- Name: tasks tasks_parent_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_parent_task_id_fkey FOREIGN KEY (parent_task_id) REFERENCES public.tasks(id);


-- Completed on 2025-09-05 16:15:52

--
-- PostgreSQL database dump complete
--

\unrestrict kq2gIdYZSHNa38fGX960WXQwNgdGCtggXUkYlpQ7H5UAGZKFEtbQv011KKRlTsd

