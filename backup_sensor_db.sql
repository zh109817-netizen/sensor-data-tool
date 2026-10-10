--
-- PostgreSQL database dump
--

\restrict l0fqW6RO8c1ePmMchZe3FkYSeYpVwuod1OUu5k8Xdb4J7945yJEooXRKQmq2fnp

-- Dumped from database version 18.6 (Debian 18.6-1.pgdg13+2)
-- Dumped by pg_dump version 18.6 (Debian 18.6-1.pgdg13+2)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: sensor_readings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sensor_readings (
    device_id text,
    ts timestamp without time zone,
    value double precision
);


ALTER TABLE public.sensor_readings OWNER TO postgres;

--
-- Data for Name: sensor_readings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sensor_readings (device_id, ts, value) FROM stdin;
sensor-01	2026-10-10 08:00:00	25.3
sensor-02	2026-10-10 08:00:05	24.9
\.


--
-- PostgreSQL database dump complete
--

\unrestrict l0fqW6RO8c1ePmMchZe3FkYSeYpVwuod1OUu5k8Xdb4J7945yJEooXRKQmq2fnp

